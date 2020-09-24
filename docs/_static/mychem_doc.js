function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

var Releases = {};
var DATA_FORMAT_VERSION = "1.0";

jQuery(document).ready(function () {
    if (jQuery(' .metadata-table ').length) {
        // get the metadata information
        jQuery.ajax({
            url: "//mychem.info/v1/metadata",
            dataType: "json",
            type: "GET",
            success: function (data) {
                // Set the total number of chems
                if (('stats' in data) && ('total' in data['stats'])) {
                    jQuery(' .metadata-table p strong ').html(numberWithCommas(data["stats"]["total"]));
                }
                jQuery.each(jQuery(' .metadata-table tbody tr '), function (index, row) {
                    var thisRow = jQuery(' .metadata-table tbody tr:nth-child(' + (index + 1).toString() + ')');
                    var thisKey = thisRow.children(' :nth-child(4) ').text();
                    if (thisKey in data["src"]) {
                        if ('version' in data['src'][thisKey]) {
                            thisRow.children(' :nth-child(2) ').html(data["src"][thisKey]["version"]);
                        }
                        if (('stats' in data['src'][thisKey]) &&
                            (thisKey in data['src'][thisKey]['stats'])) {
                            thisRow.children(' :nth-child(3) ').html(numberWithCommas(data['src'][thisKey]["stats"][thisKey]));
                        }
                    }
                });
                jQuery.ajax({
                    url: "//mychem.info/v1/metadata/fields",
                    dataType: "json",
                    type: "GET",
                    success: function (data) {
                        jQuery.each(data, function (field, d) {
                            var notes = indexed = '&nbsp;';
                            if (d.notes) { notes = d.notes; }
                            if (d.indexed) { indexed = '&#x2714'; }
                            jQuery('.indexed-field-table > tbody:last').append('<tr><td>' + field + '</td><td>' + indexed + '</td><td><span class="italic">' + d.type + '</span></td><td>' + notes + '</td>');
                        });
                        jQuery('.indexed-field-table').DataTable({
                            "iDisplayLength": 50,
                            "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                            "columns": [
                                { "width": "290px" },
                                null,
                                null,
                                null
                            ],
                            "autoWidth": false,
                            "dom": "flrtip"
                        });
                    }
                });

            }
        });
    }
    if ((jQuery('#all-releases').length)) {
        // load releases
        jQuery.ajax({
            url: 'https://biothings-releases.s3.amazonaws.com/mychem.info/versions.json',
            cache: false,
            type: "GET",
            dataType: "json",
            success: function (data, Status, jqXHR) {
                if (data.format == DATA_FORMAT_VERSION) {
                    appendResponses(Releases, data.versions);
                }
                displayReleases();
            }
        });
    }
});

function appendResponses(rel, res) {
    var done = [];
    jQuery.each(res, function (index, val) {
        var t = new Date(val["release_date"].split("T")[0].split('-'));
        if (done.indexOf(val.target_version) == -1) {
            if (!(t in rel)) { rel[t] = []; }
            rel[t].push(val);
            done.push(val.target_version);
        }
    });
}

function displayReleases() {
    // everything should be loaded and ready to display, first reverse sort all releases by date...
    var releaseDates = Object.keys(Releases);
    releaseDates.sort(function (a, b) {
        return new Date(b) - new Date(a);
    });

    // render releases
    jQuery('#all-releases').html(`
        <p class="release-control-line">
            <a href="javascript:;" class="release-expand">Expand All</a>|
            <a href="javascript:;" class="release-collapse">Collapse All</a>
        </p>`)

    jQuery.each(releaseDates, function (index, val) {

        var rDate = new Date(val)
        var tDate = rDate.toDateString().slice(4)
        var hDate = rDate.toISOString().substr(0, 10).replace(/-/g, '')

        $release = $('<div>', {
            class: "release-pane",
            id: hDate,
        })
            .append($('<h4>', {
                class: "release-date",
                text: tDate
            })
                .append($('<a>', {
                    class: "headerlink",
                    href: "#" + hDate,
                    title: "Permalink to this release",
                    text: '¶'
                })))

        jQuery.each(Releases[val], function (rIndex, rVal) {
            $release.append($('<div>')
                .append($('<a>', {
                    "href": "javascript:;",
                    "class": "release-link",
                    "data-url": rVal.url,
                    "text": 'Build version '
                })
                    .append($('<span>', {
                        class: "release-version",
                        html: rVal['target_version']
                    }))
                ).append($('<div>', {
                    class: "release-info"
                })))
        })

        jQuery('#all-releases').append($release)
    });

    // attach click handlers for each pop down link
    jQuery('.release-link').click(function () {
        if (!(jQuery(this).siblings('.release-info').hasClass('loaded'))) {
            var that = this;
            jQuery.ajax({
                url: jQuery(this).data().url,
                cache: false,
                type: "GET",
                dataType: "json",
                success: function (ndata, nStatus, njqXHR) {
                    jQuery.ajax({
                        url: ndata.changes.txt.url,
                        cache: false,
                        type: "GET",
                        success: function (edata, eStatus, ejqXHR) {
                            jQuery(that).siblings('.release-info').html('<pre>' + edata + '</pre>');
                            jQuery(that).siblings('.release-info').addClass('loaded');
                            jQuery(that).siblings('.release-info').slideToggle();
                        }
                    });
                }
            });
        }
        else {
            jQuery(this).siblings('.release-info').slideToggle();
        }
    });
    // add expand collapse click handlers
    jQuery('.release-collapse').click(function () { jQuery('.release-info').slideUp(); });
    jQuery('.release-expand').click(function () {
        jQuery('.release-info.loaded').slideDown();
        jQuery('.release-info:not(.loaded)').siblings('.release-link').click();
    });

    if (window.location.hash) {
        location.href = window.location.hash
        jQuery(window.location.hash).children("div").children("a").click()
    }
}
