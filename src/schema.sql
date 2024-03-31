CREATE DATABASE IF NOT EXISTS WSPG_DB;
USE WSPG_DB;

CREATE TABLE Department (
    DepartmentName VARCHAR(255) PRIMARY KEY,
    AvgGPA FLOAT,
    Enrollment INT,
    CourseCount INT
);

CREATE TABLE CourseInfo (
    CourseCode VARCHAR(10) NOT NULL,
    ProfessorName VARCHAR(255) NOT NULL,
    CourseTitle VARCHAR(255),
    CourseDescription TEXT,
    Credits INT,
    DepartmentName VARCHAR(255),
    PRIMARY KEY (CourseCode, ProfessorName),
    FOREIGN KEY (DepartmentName) REFERENCES Department(DepartmentName) ON DELETE CASCADE
);

CREATE TABLE ProfessorInfo (
    ProfessorName VARCHAR(255) PRIMARY KEY,
    Number5s INT,
    Number4s INT,
    Number3s INT,
    Number2s INT,
    Number1s INT
);

CREATE TABLE AverageGPA (
    CourseCode VARCHAR(10) NOT NULL,
    ProfessorName VARCHAR(255) NOT NULL,
    NumberAPlus INT,
    NumberA INT,
    NumberAMinus INT,
    NumberBPlus INT,
    NumberB INT,
    NumberBMinus INT,
    NumberCPlus INT,
    NumberC INT,
    NumberCMinus INT,
    NumberDPlus INT,
    NumberD INT,
    NumberDMinus INT,
    NumberF INT,
    NumberW INT,
    PRIMARY KEY (CourseCode, ProfessorName),
    FOREIGN KEY (CourseCode) REFERENCES CourseInfo(CourseCode), 
    FOREIGN KEY (ProfessorName) REFERENCES ProfessorInfo(ProfessorName)
);



CREATE TABLE Awards (
    ProfessorName VARCHAR(255) NOT NULL,
    Award VARCHAR(255),
    Department VARCHAR(255),
    CourseCode VARCHAR(10) NOT NULL,
    Term VARCHAR(10) NOT NULL,
    PRIMARY KEY (ProfessorName, Term),
    FOREIGN KEY (ProfessorName) REFERENCES ProfessorInfo(ProfessorName),
    FOREIGN KEY (CourseCode) REFERENCES CourseInfo(CourseCode)
);

CREATE TABLE Users (
    NetID VARCHAR(255) PRIMARY KEY,
    Major VARCHAR(255),
    GraduatingYear INT
);

CREATE TABLE MatchResult (
    NetID VARCHAR(255) NOT NULL,
    CourseCode VARCHAR(10) NOT NULL,
    Response INT,
    PRIMARY KEY (NetID, CourseCode),
    FOREIGN KEY (NetID) REFERENCES Users(NetID),
    FOREIGN KEY (CourseCode) REFERENCES CourseInfo(CourseCode)
);
