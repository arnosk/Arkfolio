"""
@author: Arno
@created: 2023-05-15
@modified: 2023-07-10

Database Schema to create tables

"""

DB_CREATE_VERSION = f"""
CREATE TABLE IF NOT EXISTS version (
    id INTEGER NOT NULL PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,
    version_timestamp INTEGER NOT NULL,
    migration_timestamp_start INTEGER NOT NULL,
    migration_timestamp_end INTEGER,
    status INTEGER
);
"""
DB_INSERT_VERSION_1 = f"""
INSERT OR IGNORE INTO version VALUES (1, '1 - Initial', strftime('%s', '2023-05-15'), strftime('%s', 'now'), NULL, 0);
"""

DB_CREATE_PROFILE = f"""
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(40) NOT NULL UNIQUE,
    password VARCHAR(80),
    enabled BOOLEAN
);
"""

DB_CREATE_SITE_TYPE = f"""
CREATE TABLE IF NOT EXISTS sitetype (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE
);
"""

DB_CREATE_SITE = f"""
CREATE TABLE IF NOT EXISTS site (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    sitetype_id INTEGER NOT NULL,
    api VARCHAR(80),
    secret VARCHAR(80),
    hasprice BOOLEAN,
    enabled BOOLEAN,
    CONSTRAINT FK_site_type FOREIGN KEY (sitetype_id) REFERENCES sitetype(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
"""

DB_CREATE_ASSET = f"""
CREATE TABLE IF NOT EXISTS asset (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(40) NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    decimal_places INTEGER NOT NULL,
    chain VARCHAR(40)
);
"""

DB_CREATE_ASSET_ON_SITE = f"""
CREATE TABLE IF NOT EXISTS assetonsite (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    id_on_site VARCHAR(40) NOT NULL,
    base VARCHAR(40),
    CONSTRAINT FK_assetonsite_asset FOREIGN KEY (asset_id) REFERENCES asset(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_assetonsite_site FOREIGN KEY (site_id) REFERENCES site(id) ON UPDATE CASCADE ON DELETE CASCADE
);
"""

DB_CREATE_SCRAPING_PRICE = f"""
CREATE TABLE IF NOT EXISTS scrapingprice (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    scrape_timestamp_start INTEGER NOT NULL,
    scrape_timestamp_end INTEGER NOT NULL,
    CONSTRAINT FK_scrapingprice_asset FOREIGN KEY (asset_id) REFERENCES asset(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_scrapingprice_site FOREIGN KEY (site_id) REFERENCES site(id) ON UPDATE CASCADE ON DELETE CASCADE
);
"""

DB_CREATE_SCRAPING_TXN = f"""
CREATE TABLE IF NOT EXISTS scrapingtxn (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    profile_id INTEGER,
    scrape_timestamp_start INTEGER NOT NULL,
    scrape_timestamp_end INTEGER NOT NULL,
    CONSTRAINT FK_scrapingtxn_site FOREIGN KEY (site_id) REFERENCES site(id) ON UPDATE CASCADE ON DELETE CASCADE
    CONSTRAINT FK_scrapingtxn_profile FOREIGN KEY (profile_id) REFERENCES profile(id) ON UPDATE CASCADE ON DELETE CASCADE
);
"""

DB_CREATE_WALLET = f"""
CREATE TABLE IF NOT EXISTS wallet (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER,
    profile_id INTEGER,
    name VARCHAR(40),
    address VARCHAR(80),
    owned BOOLEAN DEFAULT true,
    enabled BOOLEAN DEFAULT true,
    haschild BOOLEAN DEFAULT false,
    CONSTRAINT FK_wallet_site FOREIGN KEY (site_id) REFERENCES site(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_wallet_profile FOREIGN KEY (profile_id) REFERENCES profile(id) ON UPDATE CASCADE ON DELETE CASCADE
);
"""

DB_CREATE_WALLET_CHILD = f"""
CREATE TABLE IF NOT EXISTS walletchild (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NOT NULL,
    address VARCHAR(80) NOT NULL,
    used BOOLEAN NOT NULL,
    CONSTRAINT FK_wallet_parent FOREIGN KEY (parent_id) REFERENCES wallet(id) ON UPDATE CASCADE ON DELETE CASCADE
);
"""

DB_CREATE_TRANSACTION_TYPE = f"""
CREATE TABLE IF NOT EXISTS transactiontype (
    id INTEGER NOT NULL PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    subtype VARCHAR(20)
);
"""

DB_CREATE_TRANSACTION = f"""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER,
    timestamp INTEGER NOT NULL,
    transactiontype_id INTEGER NOT NULL,
    site_id INTEGER,
    from_wallet_id INTEGER,
    from_walletchild_id INTEGER,
    to_wallet_id INTEGER,
    to_walletchild_id INTEGER,
    quote_asset_id INTEGER NOT NULL,
    base_asset_id INTEGER,
    fee_asset_id INTEGER,
    quantity INTEGER,
    fee INTEGER,
    txid VARCHAR(80),
    note VARCHAR(80),
    CONSTRAINT FK_transaction_type FOREIGN KEY (transactiontype_id) REFERENCES transactiontype(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT FK_transaction_quoteasset FOREIGN KEY (quote_asset_id) REFERENCES asset(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_transaction_baseasset FOREIGN KEY (base_asset_id) REFERENCES asset(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_transaction_feeasset FOREIGN KEY (fee_asset_id) REFERENCES asset(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_transaction_site FOREIGN KEY (site_id) REFERENCES site(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_transaction_from FOREIGN KEY (from_wallet_id) REFERENCES wallet(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_transaction_fromchild FOREIGN KEY (from_walletchild_id) REFERENCES walletchild(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_transaction_to FOREIGN KEY (to_wallet_id) REFERENCES wallet(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_transaction_tochild FOREIGN KEY (to_walletchild_id) REFERENCES walletchild(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_transaction_profile FOREIGN KEY (profile_id) REFERENCES profile(id) ON UPDATE CASCADE ON DELETE CASCADE
);
"""

DB_CREATE_PRICE_HIST = f"""
CREATE TABLE IF NOT EXISTS pricehist (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    price INTEGER,
    quote_asset_id INTEGER NOT NULL,
    base_asset_id INTEGER NOT NULL,
    site_id INTEGER,
    CONSTRAINT FK_pricehist_quoteasset FOREIGN KEY (quote_asset_id) REFERENCES asset(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_pricehist_baseasset FOREIGN KEY (base_asset_id) REFERENCES asset(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_pricehist_site FOREIGN KEY (site_id) REFERENCES site(id) ON UPDATE CASCADE
);
"""


DB_SCRIPT_CREATE_TABLES = f"""
PRAGMA foreign_keys=off;
BEGIN TRANSACTION;
{DB_CREATE_VERSION}
{DB_INSERT_VERSION_1}
{DB_CREATE_PROFILE}
{DB_CREATE_SITE_TYPE}
{DB_CREATE_SITE}
{DB_CREATE_ASSET}
{DB_CREATE_ASSET_ON_SITE}
{DB_CREATE_SCRAPING_PRICE}
{DB_CREATE_SCRAPING_TXN}
{DB_CREATE_WALLET}
{DB_CREATE_WALLET_CHILD}
{DB_CREATE_TRANSACTION_TYPE}
{DB_CREATE_TRANSACTION}
{DB_CREATE_PRICE_HIST}
COMMIT;
PRAGMA foreign_keys=on;
"""
