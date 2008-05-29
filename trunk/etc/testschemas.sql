DROP TABLE IF EXISTS testshard.search;

CREATE TABLE testshard.search (
  id int(11) NOT NULL auto_increment,
  justtext text NOT NULL,
  PRIMARY KEY  (id),
  FULLTEXT KEY searchable_keyword_textsearch (justtext)
) ENGINE=MyISAM;
