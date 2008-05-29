
DROP TABLE IF EXISTS user_comment;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
       id INT NOT NULL AUTO_INCREMENT
     , userid VARCHAR(50) NOT NULL
     , firstName VARCHAR(50) NOT NULL
     , lastName VARCHAR(70) NOT NULL
     , validated BOOLEAN
     , suspended BOOLEAN
     , PRIMARY KEY (id)
) ENGINE=InnoDB ;

CREATE TABLE user_comment (
       id INT NOT NULL AUTO_INCREMENT
     , user_id INT NOT NULL
     , comment TEXT NOT NULL
     , PRIMARY KEY (id)
     , INDEX (user_id)
     , CONSTRAINT FK_user_comment_1 FOREIGN KEY (user_id)
                  REFERENCES user (id)
) ENGINE=InnoDB ;
