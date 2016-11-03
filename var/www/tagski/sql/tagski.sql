-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Nov 03, 2016 at 06:01 PM
-- Server version: 5.7.16-0ubuntu0.16.04.1
-- PHP Version: 7.0.8-0ubuntu0.16.04.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `tagski`
--
CREATE DATABASE IF NOT EXISTS `tagski` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `tagski`;

-- --------------------------------------------------------

--
-- Table structure for table `Picture`
--

DROP TABLE IF EXISTS `Picture`;
CREATE TABLE IF NOT EXISTS `Picture` (
  `Picture_id` int(10) NOT NULL AUTO_INCREMENT,
  `Location` varchar(1000) NOT NULL COMMENT 'Full path and filename',
  `Thumbnail` varchar(1000) NOT NULL COMMENT 'Full path of generated thumbnail',
  PRIMARY KEY (`Picture_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `PictureTag`
--

DROP TABLE IF EXISTS `PictureTag`;
CREATE TABLE IF NOT EXISTS `PictureTag` (
  `PictureTag_id` int(10) NOT NULL AUTO_INCREMENT,
  `Picture_id` int(10) NOT NULL,
  `Tag_id` int(10) NOT NULL,
  PRIMARY KEY (`PictureTag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Tag`
--

DROP TABLE IF EXISTS `Tag`;
CREATE TABLE IF NOT EXISTS `Tag` (
  `Tag_id` int(10) NOT NULL AUTO_INCREMENT,
  `TagText` varchar(1000) NOT NULL,
  PRIMARY KEY (`Tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
