CREATE SCHEMA IF NOT EXISTS `student_rating`;
use student_rating;
CREATE TABLE IF NOT EXISTS `user` (
  `id_user` INT NOT NULL AUTO_INCREMENT,
  `user_name` VARCHAR(25) NOT NULL,
  `password` VARCHAR(25) NOT NULL,
  `first_name` VARCHAR(25) NOT NULL,
  `last_name` VARCHAR(25) NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  `phone` VARCHAR(25) NOT NULL,
  PRIMARY KEY (`id_user`),
  UNIQUE INDEX `user_name_UNIQUE` (`user_name` ASC) VISIBLE);




CREATE TABLE IF NOT EXISTS `group` (
  `id_group` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(25) NOT NULL,
  PRIMARY KEY (`id_group`));



CREATE TABLE IF NOT EXISTS `student` (
  `user_id` INT NOT NULL,
  `date_of_birthday` DATE NOT NULL,
  `date_of_entry` DATE NOT NULL,
  `date_of_graduation` DATE NOT NULL,
  `group_id` INT NOT NULL,
  PRIMARY KEY (`user_id`, `group_id`),
  INDEX `fk_student_user1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_student_group1_idx` (`group_id` ASC) VISIBLE,
  CONSTRAINT `fk_student_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`id_user`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_student_group1`
    FOREIGN KEY (`group_id`)
    REFERENCES `group` (`id_group`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);




CREATE TABLE IF NOT EXISTS `teacher` (
  `user_id` INT NOT NULL,
  `date_of_employment` DATE NOT NULL,
  `qualification` VARCHAR(75) NOT NULL,
  PRIMARY KEY (`user_id`),
  INDEX `fk_teacher_user1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_teacher_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`id_user`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);



CREATE TABLE IF NOT EXISTS `subject` (
  `id_subject` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `credits` INT NOT NULL,
  PRIMARY KEY (`id_subject`));



CREATE TABLE IF NOT EXISTS `mark` (
  `id_mark` INT NOT NULL AUTO_INCREMENT,
  `mark` INT NOT NULL,
  `date` DATE NOT NULL,
  `subject_id` INT NOT NULL,
  `student_id` INT NOT NULL,
  `teacher_id` INT NOT NULL,
  PRIMARY KEY (`id_mark`, `subject_id`, `student_id`, `teacher_id`),
  INDEX `fk_mark_subject1_idx` (`subject_id` ASC) VISIBLE,
  INDEX `fk_mark_student1_idx` (`student_id` ASC) VISIBLE,
  INDEX `fk_mark_teacher1_idx` (`teacher_id` ASC) VISIBLE,
  CONSTRAINT `fk_mark_subject1`
    FOREIGN KEY (`subject_id`)
    REFERENCES `subject` (`id_subject`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_mark_student1`
    FOREIGN KEY (`student_id`)
    REFERENCES `student` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_mark_teacher1`
    FOREIGN KEY (`teacher_id`)
    REFERENCES `teacher` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);