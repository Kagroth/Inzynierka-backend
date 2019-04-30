/* table UserType */
CREATE TABLE public."UserType"
(
    "UserTypeId" serial NOT NULL,
    "Name" character varying(32) NOT NULL,
    PRIMARY KEY ("UserTypeId")
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."UserType"
    OWNER to postgres;
	
	
/* table Users */
CREATE TABLE public."Users"
(
    "UserId" serial NOT NULL,
    "UserTypeId" integer NOT NULL,
    "Login" character varying(32) NOT NULL,
    "Password" character varying(64) NOT NULL,
    "Email" character varying(32) NOT NULL,
    PRIMARY KEY ("UserId"),
    FOREIGN KEY ("UserTypeId")
        REFERENCES public."UserType" ("UserTypeId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Users"
    OWNER to postgres;

	
/* table UserGroup */	
CREATE TABLE public."UserGroup"
(
    "UserGroupId" serial NOT NULL,
    "Name" character varying(32) NOT NULL,
    PRIMARY KEY ("UserGroupId")
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."UserGroup"
    OWNER to postgres;

	
/* table Users_UserGroup - tabela laczaca */
CREATE TABLE public."Users_UserGroup"
(
    "UserId" integer NOT NULL,
    "UserGroupId" integer NOT NULL,
    PRIMARY KEY ("UserId", "UserGroupId"),
    FOREIGN KEY ("UserId")
        REFERENCES public."Users" ("UserId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Users_UserGroup"
    OWNER to postgres;

	
/*table Exercise */
CREATE TABLE public."Exercise"
(
    "ExerciseId" serial NOT NULL,
    "Title" character varying(128) NOT NULL,
    "Language" character varying(32) NOT NULL,
    "Content" text NOT NULL,
    "Level" integer NOT NULL,
    PRIMARY KEY ("ExerciseId")
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Exercise"
    OWNER to postgres;

	
/* table UnitTest */
CREATE TABLE public."UnitTest"
(
    "UnitTestId" serial NOT NULL,
    "PathToFile" character varying(128) NOT NULL,
    "ExerciseId" integer NOT NULL,
    PRIMARY KEY ("UnitTestId"),
    FOREIGN KEY ("ExerciseId")
        REFERENCES public."Exercise" ("ExerciseId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."UnitTest"
    OWNER to postgres;
	
	
/* table Test */
CREATE TABLE public."Test"
(
    "TestId" serial NOT NULL,
    "Name" character varying(64) NOT NULL,
    PRIMARY KEY ("TestId")
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Test"
    OWNER to postgres;
	
		
/* table Exercise_Test - tabela laczaca */
CREATE TABLE public."Exercise_Test"
(
    "ExerciseId" integer NOT NULL,
    "TestId" integer NOT NULL,
    PRIMARY KEY ("ExerciseId", "TestId"),
    FOREIGN KEY ("ExerciseId")
        REFERENCES public."Exercise" ("ExerciseId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY ("TestId")
        REFERENCES public."Test" ("TestId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Exercise_Test"
    OWNER to postgres;	
	
	
/* table TaskType */
CREATE TABLE public."TaskType"
(
    "TaskTypeId" serial NOT NULL,
    "Name" character varying(32) NOT NULL,
    PRIMARY KEY ("TaskTypeId")
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."TaskType"
    OWNER to postgres;


/* table Task */	
CREATE TABLE public."Task"
(
    "TaskId" serial NOT NULL,
    "TaskTypeId" integer NOT NULL,
    "ExerciseId" integer,
    "TestId" integer,
    PRIMARY KEY ("TaskId"),
    FOREIGN KEY ("TaskTypeId")
        REFERENCES public."TaskType" ("TaskTypeId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY ("ExerciseId")
        REFERENCES public."Exercise" ("ExerciseId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY ("TestId")
        REFERENCES public."Test" ("TestId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE RESTRICT
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public."Task"
    OWNER to postgres;


/* table Solution */
CREATE TABLE public."Solution"
(
    "SolutionId" serial NOT NULL,
    "PathToFile" character varying(128) NOT NULL,
    "TaskId" integer NOT NULL,
    "UserId" integer NOT NULL,
    "Rate" smallint,
    PRIMARY KEY ("SolutionId"),
    FOREIGN KEY ("TaskId")
        REFERENCES public."Task" ("TaskId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY ("UserId")
        REFERENCES public."Users" ("UserId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE RESTRICT
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Solution"
    OWNER to postgres;

/* table UserGroup_Task - tabela laczaca */
CREATE TABLE public."UserGroup_Task"
(
    "UserGroupId" integer NOT NULL,
    "TaskId" integer NOT NULL,
    PRIMARY KEY ("UserGroupId", "TaskId"),
    FOREIGN KEY ("UserGroupId")
        REFERENCES public."UserGroup" ("UserGroupId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY ("TaskId")
        REFERENCES public."Task" ("TaskId") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."UserGroup_Task"
    OWNER to postgres;