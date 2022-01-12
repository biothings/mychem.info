#!/bin/bash

#Usage ./dump_tables.sh <drugcentral_dump.sql>

CONN_STR="psql -h localhost -p 5432 -U $USER"
database="drugcentral_new"

# Create database
$CONN_STR -c "create database $database"
# Import SQL dump
$CONN_STR -d $database -c "\i $1"

# Download data tables as csv
$CONN_STR -d $database -c "\copy (select * from pharma_class) TO pharma_class.csv DELIMITER ',' CSV HEADER;"
$CONN_STR -d $database -c "\copy (select * from faers) TO faers.csv DELIMITER ',' CSV HEADER;"
$CONN_STR -d $database -c "\copy (select * from act_table_full) TO act_table_full.csv DELIMITER ',' CSV HEADER;"
$CONN_STR -d $database -c "\copy (select * from omop_relationship) TO omop_relationship.csv DELIMITER ',' CSV HEADER;"
$CONN_STR -d $database -c "\copy (select * from approval) TO approval.csv DELIMITER ',' CSV HEADER;"
$CONN_STR -d $database -c "\copy (select * from atc_ddd) TO drug_dosage.csv DELIMITER ',' CSV HEADER;"
$CONN_STR -d $database -c "\copy (select * from synonyms) TO syonyms.csv DELIMITER ',' CSV HEADER;"
$CONN_STR -d $database -c "\copy (select id, inchi, inchikey, smiles, cas_reg_no, name from structures) TO structures.smiles.csv DELIMITER ',' CSV HEADER;"
$CONN_STR -d $database -c "\copy (select * from identifier) TO identifiers.csv DELIMITER ',' CSV HEADER;"