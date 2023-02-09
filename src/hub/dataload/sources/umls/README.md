## UMLS File Dumping

Note that the `umls_dumper.py` only dumps the [UMLS Release Note](https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/notes.html) as a dummy file (to trigger the automatic uploading).

It also parses the [UMLS File Downloads](https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html) HTML document for the latest `release` tag. E.g. `2022AB` UMLS Metathesaurus was released on November 7, 2022, which `umls_dumper.py` parses to `2022-11-07`. This `release` tag is used as the `umls.version` in the metadata.

However, `umls_dumper.py` is not designed to download the two RRF files, `MRCONSO.RRF` and `MRSTY.RRF`, that the `umls_parser.py` actually needs. It's the hub users' job to manually download these two files, and to place them to the correct data folder.

## Downloading Script

`download.sh` is a script to download UMLS resources (credit to _StackExchange_ user [Gopalakrishna Palem](https://unix.stackexchange.com/a/624877)). It should be executed in the following way:

```bash
bash download.sh <API_KEY> <DOWNLOAD_URL>
```

Information on UMLS API keys can be found at [UMLS User Authentication](https://documentation.uts.nlm.nih.gov/rest/authentication.html).

**Note:** Sometimes UMLS login may fail in Chrome (possibly due to language settings). Try other browsers if this happened.

Download URLs should not contain any query string, i.e. all characters following the question mark in a URL should be removed. E.g. the following URL for `mls-2022AB-metathesaurus-level-0.zip` does not work with the script.

```txt
https://download.nlm.nih.gov/umls/kss/2022AB/umls-2022AB-metathesaurus-level-0.zip?_gl=1*r2vyt*_ga*MTc0MTg4OTcxOS4xNjY1NDUyMTQ1*_ga_7147EPK006*MTY3NTk3OTQ3Ni4zNy4xLjE2NzU5ODIxMDYuMC4wLjA.*_ga_P1FPTH9PL4*MTY3NTk3OTQ3Ni4zNi4xLjE2NzU5ODIxMDYuMC4wLjA.
```

Instead, the following URL works well.

```txt
https://download.nlm.nih.gov/umls/kss/2022AB/umls-2022AB-metathesaurus-level-0.zip
```

Since the `2022AB` release, the `UMLS Metathesaurus Level 0 Subset` zip file already contains the two RRF files and it's not necessary to download the larger `UMLS Metathesaurus Full Subset`.