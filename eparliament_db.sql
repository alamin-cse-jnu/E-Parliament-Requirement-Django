-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 13, 2025 at 09:40 PM
-- Server version: 11.7.2-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `eparliament_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add form section', 6, 'add_formsection'),
(22, 'Can change form section', 6, 'change_formsection'),
(23, 'Can delete form section', 6, 'delete_formsection'),
(24, 'Can view form section', 6, 'view_formsection'),
(25, 'Can add user', 7, 'add_user'),
(26, 'Can change user', 7, 'change_user'),
(27, 'Can delete user', 7, 'delete_user'),
(28, 'Can view user', 7, 'view_user'),
(29, 'Can add form question', 8, 'add_formquestion'),
(30, 'Can change form question', 8, 'change_formquestion'),
(31, 'Can delete form question', 8, 'delete_formquestion'),
(32, 'Can view form question', 8, 'view_formquestion'),
(33, 'Can add requirement form', 9, 'add_requirementform'),
(34, 'Can change requirement form', 9, 'change_requirementform'),
(35, 'Can delete requirement form', 9, 'delete_requirementform'),
(36, 'Can view requirement form', 9, 'view_requirementform'),
(37, 'Can add form response', 10, 'add_formresponse'),
(38, 'Can change form response', 10, 'change_formresponse'),
(39, 'Can delete form response', 10, 'delete_formresponse'),
(40, 'Can view form response', 10, 'view_formresponse'),
(41, 'Can add question response', 11, 'add_questionresponse'),
(42, 'Can change question response', 11, 'change_questionresponse'),
(43, 'Can delete question response', 11, 'delete_questionresponse'),
(44, 'Can view question response', 11, 'view_questionresponse');

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2025-04-05 09:01:26.911676', '2', '110100091 - Al-Amin Hossain', 1, '[{\"added\": {}}]', 7, 1),
(2, '2025-04-05 09:46:27.330695', '1', 'Current Workflow - Current software or manual process used (if any):', 1, '[{\"added\": {}}]', 8, 1);

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(8, 'requirements_app', 'formquestion'),
(10, 'requirements_app', 'formresponse'),
(6, 'requirements_app', 'formsection'),
(11, 'requirements_app', 'questionresponse'),
(9, 'requirements_app', 'requirementform'),
(7, 'requirements_app', 'user'),
(5, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-04-05 08:56:58.501693'),
(2, 'contenttypes', '0002_remove_content_type_name', '2025-04-05 08:56:58.535661'),
(3, 'auth', '0001_initial', '2025-04-05 08:56:58.660436'),
(4, 'auth', '0002_alter_permission_name_max_length', '2025-04-05 08:56:58.685064'),
(5, 'auth', '0003_alter_user_email_max_length', '2025-04-05 08:56:58.688520'),
(6, 'auth', '0004_alter_user_username_opts', '2025-04-05 08:56:58.691696'),
(7, 'auth', '0005_alter_user_last_login_null', '2025-04-05 08:56:58.695031'),
(8, 'auth', '0006_require_contenttypes_0002', '2025-04-05 08:56:58.696286'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2025-04-05 08:56:58.699125'),
(10, 'auth', '0008_alter_user_username_max_length', '2025-04-05 08:56:58.702382'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2025-04-05 08:56:58.705658'),
(12, 'auth', '0010_alter_group_name_max_length', '2025-04-05 08:56:58.720436'),
(13, 'auth', '0011_update_proxy_permissions', '2025-04-05 08:56:58.724346'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2025-04-05 08:56:58.727657'),
(15, 'requirements_app', '0001_initial', '2025-04-05 08:56:59.115809'),
(16, 'admin', '0001_initial', '2025-04-05 08:56:59.184388'),
(17, 'admin', '0002_logentry_remove_auto_add', '2025-04-05 08:56:59.191146'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2025-04-05 08:56:59.196449'),
(19, 'sessions', '0001_initial', '2025-04-05 08:56:59.225727'),
(20, 'requirements_app', '0002_requirementform_current_process_and_more', '2025-04-05 10:49:45.189907'),
(21, 'requirements_app', '0003_requirementform_attachment', '2025-04-07 14:02:21.587203'),
(22, 'requirements_app', '0004_requirementform_flowchart', '2025-04-09 11:26:32.224346'),
(23, 'requirements_app', '0005_requirementform_digital_limitation_and_more', '2025-04-09 14:57:05.270404'),
(24, 'requirements_app', '0006_alter_requirementform_digital_limitation_and_more', '2025-04-09 15:11:12.554604'),
(25, 'requirements_app', '0007_remove_requirementform_current_process_and_more', '2025-04-10 15:18:53.496908'),
(26, 'requirements_app', '0008_alter_requirementform_ease_of_access_and_more', '2025-04-10 15:42:59.830643'),
(27, 'requirements_app', '0009_alter_requirementform_external_connectivity_details_and_more', '2025-04-12 05:57:46.214363'),
(28, 'requirements_app', '0010_alter_requirementform_ease_of_access_and_more', '2025-04-13 14:45:58.128390'),
(29, 'requirements_app', '0011_remove_requirementform_ease_of_access_and_more', '2025-04-13 14:45:58.171849'),
(30, 'requirements_app', '0012_requirementform_process_steps_detail', '2025-04-13 17:36:44.733318');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('0fvord8n9p1batf8pgqoi0msdxcwzegk', '.eJxVjEEOwiAQRe_C2hBgkI4u3fcMZMoMUjU0Ke3KeHfbpAvd_vfef6tI61Li2mSOI6urAnX63QZKT6k74AfV-6TTVJd5HPSu6IM23U8sr9vh_h0UamWrOyERxmRSAEKwaATD2XOXQSh4YyFhcs7kDACIzmdiDk6syxfZNPX5AvAbOAk:1u156m:NV_VXDaih9_3fvsSJ3DVRZ9eGH09P63CD3q9Df6xvoc', '2025-04-05 16:06:56.980955'),
('2jbgxesetb6924pw9uuc4i06rm3wquro', '.eJxVjDsOwyAQBe9CHSHAfEzK9D4DWtglOIlAMnYV5e6xJRdJ-2bmvVmAbS1h67SEGdmVaXb53SKkJ9UD4APqvfHU6rrMkR8KP2nnU0N63U7376BAL3vtRuvRGlDKUcpo9ehhEEmS9ChjFhBt9mbYgfEGMGoiAoXGWBdBWGSfL-uZOHA:1u2YD7:y3ZopWk0WhTJJ7p2vmbk1bMHOeBvRV3vx7qn5NtmVkg', '2025-04-09 17:23:33.071023'),
('40u5dlbu50cwb4bsxcfkhhocjjbykh8n', '.eJxVjDsOwyAQBe9CHSHAfEzK9D4DWtglOIlAMnYV5e6xJRdJ-2bmvVmAbS1h67SEGdmVaXb53SKkJ9UD4APqvfHU6rrMkR8KP2nnU0N63U7376BAL3vtRuvRGlDKUcpo9ehhEEmS9ChjFhBt9mbYgfEGMGoiAoXGWBdBWGSfL-uZOHA:1u2TVb:rMOeR5JNHJAs9dFS4OfmFizpeDoZz9TVPoxuwT4EmW4', '2025-04-09 12:22:19.846781'),
('9stsghpvju0r1cifbule056k1y2nmzps', '.eJxVjE0OwiAYRO_C2hAKQdCle89Avj-kamhS2lXj3aVJF7qceW9mUwnWpaS1yZxGVldl1em3Q6CX1B3wE-pj0jTVZR5R74o-aNP3ieV9O9y_gwKt9HVEHwKiDJSNhUxCPUYfAwTrghOJAwv1YOiCljI5RiY8ewjGZ3bq8wURyTlR:1u2Roh:mDytl_27D1EUskYn3r8RgnsHgnn0a1fvrk8CL4-c3Ck', '2025-04-09 10:33:55.387063'),
('c47tpoi0upq72rp4u6qm83lk29b40ddf', '.eJxVjDsOwyAQBe9CHSHAfEzK9D4DWtglOIlAMnYV5e6xJRdJ-2bmvVmAbS1h67SEGdmVaXb53SKkJ9UD4APqvfHU6rrMkR8KP2nnU0N63U7376BAL3vtRuvRGlDKUcpo9ehhEEmS9ChjFhBt9mbYgfEGMGoiAoXGWBdBWGSfL-uZOHA:1u1obL:KCwi3cuugYNY-Uod-nLMcp6izK6gJJx3wFBg9VzGDCk', '2025-04-07 16:41:31.554176'),
('cc05i19vag3nb87wfl8q3osnrjwvkltt', '.eJxVjDsOwyAQBe9CHSHAfEzK9D4DWtglOIlAMnYV5e6xJRdJ-2bmvVmAbS1h67SEGdmVaXb53SKkJ9UD4APqvfHU6rrMkR8KP2nnU0N63U7376BAL3vtRuvRGlDKUcpo9ehhEEmS9ChjFhBt9mbYgfEGMGoiAoXGWBdBWGSfL-uZOHA:1u3U7y:PgW42wgKH2jd28_7ofNUkJAl1s5OL9x4WVNtlWOKQAo', '2025-04-12 07:14:06.140048'),
('cfp5shc1n5cazs6a5s0wzpa1kbietiag', '.eJxVjEEOwiAQRe_C2hBgkI4u3fcMZMoMUjU0Ke3KeHfbpAvd_vfef6tI61Li2mSOI6urAnX63QZKT6k74AfV-6TTVJd5HPSu6IM23U8sr9vh_h0UamWrOyERxmRSAEKwaATD2XOXQSh4YyFhcs7kDACIzmdiDk6syxfZNPX5AvAbOAk:1u11T4:FHJJG__C-gKy7MlZWAYIRtgrZFUQHllwqOks9EFTXLM', '2025-04-05 12:13:42.885637'),
('e5klctyl34gqwctyuqkpjuqanx46fh8a', '.eJxVjMsOwiAQRf-FtSEMb1y69xsIA4xUDU1KuzL-uzbpQrf3nHNfLKZtbXEbdYlTYWcm2el3w5Qfte-g3FO_zTzPfV0m5LvCDzr4dS71eTncv4OWRvvWLiGSFU57AwDeOqNUzd6mghRQCyCtvTeSTFBkwGZjpUAggOAtoWLvD8cMNu8:1u10tT:TndgwlHl9iU1fmvoW8rpEge5tFN_JjQJ_wmtP_jgcvk', '2025-04-05 11:36:55.027882'),
('f5f4hrc0b18d3yidcygstftg68hf9iq3', '.eJxVjDsOwyAQBe9CHSHAfEzK9D4DWtglOIlAMnYV5e6xJRdJ-2bmvVmAbS1h67SEGdmVaXb53SKkJ9UD4APqvfHU6rrMkR8KP2nnU0N63U7376BAL3vtRuvRGlDKUcpo9ehhEEmS9ChjFhBt9mbYgfEGMGoiAoXGWBdBWGSfL-uZOHA:1u437m:gvNXxR0jUyG2FOedH-mtwS2r1yZE9ZEJ7WbWaEH6zyE', '2025-04-13 20:36:14.352183'),
('fnd782zmjlpax93lph53gx7antw5y9nu', '.eJxVjDsOwyAQBe9CHSHAfEzK9D4DWtglOIlAMnYV5e6xJRdJ-2bmvVmAbS1h67SEGdmVaXb53SKkJ9UD4APqvfHU6rrMkR8KP2nnU0N63U7376BAL3vtRuvRGlDKUcpo9ehhEEmS9ChjFhBt9mbYgfEGMGoiAoXGWBdBWGSfL-uZOHA:1u3WSF:CtzlcZrs1INCF6XZpSh5nUJZ4Lf9l60hAeAkICi232Q', '2025-04-12 09:43:11.259425'),
('i9sy4libtp2a4y20yt6bf9on6yaz8pmh', '.eJxVjDsOwyAQBe9CHSHAfEzK9D4DWtglOIlAMnYV5e6xJRdJ-2bmvVmAbS1h67SEGdmVaXb53SKkJ9UD4APqvfHU6rrMkR8KP2nnU0N63U7376BAL3vtRuvRGlDKUcpo9ehhEEmS9ChjFhBt9mbYgfEGMGoiAoXGWBdBWGSfL-uZOHA:1u2uPE:-xA5EBsvoPZtVboN70-WgpK9rsjPtKeGfV-rfJhhmwE', '2025-04-10 17:05:32.111235'),
('ipo223ov007udxx476tlyzybv46w5rjp', '.eJxVjE0OwiAYRO_C2hAKQdCle89Avj-kamhS2lXj3aVJF7qceW9mUwnWpaS1yZxGVldl1em3Q6CX1B3wE-pj0jTVZR5R74o-aNP3ieV9O9y_gwKt9HVEHwKiDJSNhUxCPUYfAwTrghOJAwv1YOiCljI5RiY8ewjGZ3bq8wURyTlR:1u3zCc:BSwsBxNqd8JK0ZTjADJLFu9GtsA5OdRqUksMAaPho9E', '2025-04-13 16:24:58.776264'),
('k3geqan9njjv7qar0u3uqupqmuyu11lj', '.eJxVjDsOwyAQBe9CHSHAfEzK9D4DWtglOIlAMnYV5e6xJRdJ-2bmvVmAbS1h67SEGdmVaXb53SKkJ9UD4APqvfHU6rrMkR8KP2nnU0N63U7376BAL3vtRuvRGlDKUcpo9ehhEEmS9ChjFhBt9mbYgfEGMGoiAoXGWBdBWGSfL-uZOHA:1u3JCF:vfpLo5COY9duuhIoIvY1COCADvPeNuj0OFxv45Vy13E', '2025-04-11 19:33:47.224485'),
('ngui1fujxb7v294uxhwlo0rvlbl5h9ev', '.eJxVjDkOwjAUBe_iGlnxblPScwbLfxEOIFuKkwpxd4iUAto3M-8lctnWmrfBS55JnIUSp98NCj647YDupd26xN7WZQa5K_KgQ1478fNyuH8HtYz6ra0LqKdkdCRECKQjO0xBcSplQsJkvYeolbae2BomCgFUAucQvPNGvD_iSDff:1u1Rg1:bLVjsys4rpvnfUSE9JVfn4AHbtoDaNfvAaNYofdI5tQ', '2025-04-06 16:12:49.877886'),
('nq2jn29hhk5ubs6upiseoi8pl49oorzx', '.eJxVjDsOwyAQBe9CHSHAfEzK9D4DWtglOIlAMnYV5e6xJRdJ-2bmvVmAbS1h67SEGdmVaXb53SKkJ9UD4APqvfHU6rrMkR8KP2nnU0N63U7376BAL3vtRuvRGlDKUcpo9ehhEEmS9ChjFhBt9mbYgfEGMGoiAoXGWBdBWGSfL-uZOHA:1u3Icq:Zy2MONHkQFZgiNfKY2xJwTDPPBqdHcbpPJOnpF3bAUo', '2025-04-11 18:57:12.131365'),
('orfxem1ix1z0vay1plek9tckogjk2kkg', '.eJxVjE0OwiAYRO_C2hAKQdCle89Avj-kamhS2lXj3aVJF7qceW9mUwnWpaS1yZxGVldl1em3Q6CX1B3wE-pj0jTVZR5R74o-aNP3ieV9O9y_gwKt9HVEHwKiDJSNhUxCPUYfAwTrghOJAwv1YOiCljI5RiY8ewjGZ3bq8wURyTlR:1u2tmd:Xsu7cJywFiFiArOE_OffkOKpXFvUGFipyBgUK-7Aq8M', '2025-04-10 16:25:39.087354'),
('otz6m2w124wn2x8a5fkzxmya13stab41', '.eJxVjE0OwiAYRO_C2hAKQdCle89Avj-kamhS2lXj3aVJF7qceW9mUwnWpaS1yZxGVldl1em3Q6CX1B3wE-pj0jTVZR5R74o-aNP3ieV9O9y_gwKt9HVEHwKiDJSNhUxCPUYfAwTrghOJAwv1YOiCljI5RiY8ewjGZ3bq8wURyTlR:1u2VpB:6y1EaK4AOzKrvuVF0SyUae8v5e0oFhOQmZ5AnnHkZOw', '2025-04-09 14:50:41.006815'),
('phvmgehsvbawytl92jw4djq8j2joi1h2', '.eJxVjDsOwyAQBe9CHSHAfEzK9D4DWtglOIlAMnYV5e6xJRdJ-2bmvVmAbS1h67SEGdmVaXb53SKkJ9UD4APqvfHU6rrMkR8KP2nnU0N63U7376BAL3vtRuvRGlDKUcpo9ehhEEmS9ChjFhBt9mbYgfEGMGoiAoXGWBdBWGSfL-uZOHA:1u1nsi:XuhIJmcOhyoWgLWBjx3qmoH8JKqgVkxvBCy4OVI_ui0', '2025-04-07 15:55:24.938617'),
('shleulng3fng1lolrnrtg4xostohkmdk', '.eJxVjE0OwiAYRO_C2hAKQdCle89Avj-kamhS2lXj3aVJF7qceW9mUwnWpaS1yZxGVldl1em3Q6CX1B3wE-pj0jTVZR5R74o-aNP3ieV9O9y_gwKt9HVEHwKiDJSNhUxCPUYfAwTrghOJAwv1YOiCljI5RiY8ewjGZ3bq8wURyTlR:1u3dm9:5o1rFy_EliEKVY-H4WPyDQQ5If-IDBMARWuxxXUTXLk', '2025-04-12 17:32:13.024559'),
('sollzjs1426wtzu5o90ps89x77mdbu9z', '.eJxVjE0OwiAYRO_C2hAKQdCle89Avj-kamhS2lXj3aVJF7qceW9mUwnWpaS1yZxGVldl1em3Q6CX1B3wE-pj0jTVZR5R74o-aNP3ieV9O9y_gwKt9HVEHwKiDJSNhUxCPUYfAwTrghOJAwv1YOiCljI5RiY8ewjGZ3bq8wURyTlR:1u41wN:RfQ4lJUV6thwjlDtopiG3voUhU4B1zxahg_GBEi89x0', '2025-04-13 19:20:23.998362');

-- --------------------------------------------------------

--
-- Table structure for table `requirements_app_formquestion`
--

CREATE TABLE `requirements_app_formquestion` (
  `id` bigint(20) NOT NULL,
  `question_text` varchar(500) NOT NULL,
  `field_type` varchar(20) NOT NULL,
  `options` longtext NOT NULL,
  `is_required` tinyint(1) NOT NULL,
  `order` int(11) NOT NULL,
  `help_text` varchar(255) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `section_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `requirements_app_formquestion`
--

INSERT INTO `requirements_app_formquestion` (`id`, `question_text`, `field_type`, `options`, `is_required`, `order`, `help_text`, `is_active`, `section_id`) VALUES
(4, 'Anything else you want to mention:', 'textarea', '', 0, 1, '', 1, 4);

-- --------------------------------------------------------

--
-- Table structure for table `requirements_app_formresponse`
--

CREATE TABLE `requirements_app_formresponse` (
  `id` bigint(20) NOT NULL,
  `answer` longtext NOT NULL,
  `question_id` bigint(20) NOT NULL,
  `form_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `requirements_app_formsection`
--

CREATE TABLE `requirements_app_formsection` (
  `id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `order` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `requirements_app_formsection`
--

INSERT INTO `requirements_app_formsection` (`id`, `title`, `description`, `order`, `is_active`, `created_at`, `updated_at`) VALUES
(4, 'Section E: Additional Comment', '', 1, 1, '2025-04-10 15:23:59.354105', '2025-04-10 15:25:39.073616');

-- --------------------------------------------------------

--
-- Table structure for table `requirements_app_questionresponse`
--

CREATE TABLE `requirements_app_questionresponse` (
  `id` bigint(20) NOT NULL,
  `response_text` longtext NOT NULL,
  `question_id` bigint(20) NOT NULL,
  `form_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `requirements_app_requirementform`
--

CREATE TABLE `requirements_app_requirementform` (
  `id` bigint(20) NOT NULL,
  `process_name` varchar(100) NOT NULL,
  `status` varchar(10) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `submitted_at` datetime(6) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  `attachment` varchar(100) DEFAULT NULL,
  `flowchart` varchar(100) DEFAULT NULL,
  `expected_analysis` longtext NOT NULL,
  `expected_features` longtext NOT NULL,
  `expected_reports` longtext NOT NULL,
  `external_connectivity` varchar(10) NOT NULL,
  `external_connectivity_details` longtext NOT NULL,
  `internal_connectivity` varchar(10) NOT NULL,
  `internal_connectivity_details` longtext NOT NULL,
  `people_involved` int(10) UNSIGNED NOT NULL,
  `process_description` longtext NOT NULL,
  `process_steps` int(10) UNSIGNED NOT NULL,
  `time_taken` int(10) UNSIGNED NOT NULL,
  `process_steps_detail` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`process_steps_detail`))
) ;

-- --------------------------------------------------------

--
-- Table structure for table `requirements_app_user`
--

CREATE TABLE `requirements_app_user` (
  `id` bigint(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(10) NOT NULL,
  `designation` varchar(100) NOT NULL,
  `wing_name` varchar(100) NOT NULL,
  `department_name` varchar(100) NOT NULL,
  `section_name` varchar(100) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `photo` varchar(100) DEFAULT NULL,
  `signature` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `requirements_app_user`
--

INSERT INTO `requirements_app_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`, `designation`, `wing_name`, `department_name`, `section_name`, `mobile`, `photo`, `signature`) VALUES
(1, 'pbkdf2_sha256$870000$jPxkCyQxKzfOikUnxyPIYO$HqmRQ/J452pgomkmSwrFtJ9WCdbsRxLbY3VoWkRcKTU=', '2025-04-09 11:16:51.133545', 1, 'alamin', '', '', 'alamin@gmail.com', 1, 1, '2025-04-05 08:58:10.412461', 'user', '', '', '', '', '', '', ''),
(2, 'pbkdf2_sha256$870000$MABututGmqJhqYn4JUDj5G$BeKSUdePlUbpCfzVkJFu5+qu+YCieu1zRgcsC5rtRpw=', '2025-04-13 17:57:46.741033', 0, '110100091', 'Al-Amin', 'Hossain', '', 0, 1, '2025-04-05 09:01:26.518627', 'admin', 'Programmer', 'B&IT', 'IT', 'Software Development', '01914219285', 'photos/user_None.jpg', 'signatures/user_None.jpg'),
(3, 'pbkdf2_sha256$870000$GuQ1vhBdQ2FsejhT1yIwxC$fM6rSFqNervmcGkBsx2i3qZTpCQ3CkKNXD577NLu6SY=', '2025-04-05 15:06:31.210947', 0, '110100092', 'Azad', 'Kalam', 'nikhil@ewubd.edu', 0, 1, '2025-04-05 09:05:40.052748', 'user', 'Professor', 'F&PR', 'Finance', 'Finance-2', '01932382816', 'photos/user_3.jpg', 'signatures/user_3.jpg'),
(4, 'pbkdf2_sha256$870000$5k1E03ewL3VGR464oWIFeB$q8LFHlmwtIMrKIRgSVXNX0wVl1AiuwidtImRwph3aWw=', '2025-04-13 15:12:39.215773', 0, '110100060', 'Ashif', 'Iqbal', 'learning.fba.amz@gmail.com', 0, 1, '2025-04-07 14:03:52.390435', 'user', 'Director', 'B&IT', 'System Management', 'N/A', '01932382816', 'photos/user_4_FlFnp1V.JPG', 'signatures/user_4_iVlTn0d.JPG');

-- --------------------------------------------------------

--
-- Table structure for table `requirements_app_user_groups`
--

CREATE TABLE `requirements_app_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `requirements_app_user_user_permissions`
--

CREATE TABLE `requirements_app_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_requirements_app_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `requirements_app_formquestion`
--
ALTER TABLE `requirements_app_formquestion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `requirements_app_for_section_id_77b7f781_fk_requireme` (`section_id`);

--
-- Indexes for table `requirements_app_formresponse`
--
ALTER TABLE `requirements_app_formresponse`
  ADD PRIMARY KEY (`id`),
  ADD KEY `requirements_app_for_question_id_92dbb5ff_fk_requireme` (`question_id`),
  ADD KEY `requirements_app_for_form_id_617f265d_fk_requireme` (`form_id`);

--
-- Indexes for table `requirements_app_formsection`
--
ALTER TABLE `requirements_app_formsection`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `requirements_app_questionresponse`
--
ALTER TABLE `requirements_app_questionresponse`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `requirements_app_questio_form_id_question_id_8c6e90a6_uniq` (`form_id`,`question_id`),
  ADD KEY `requirements_app_que_question_id_c5bfc83f_fk_requireme` (`question_id`);

--
-- Indexes for table `requirements_app_requirementform`
--
ALTER TABLE `requirements_app_requirementform`
  ADD PRIMARY KEY (`id`),
  ADD KEY `requirements_app_req_user_id_c66d5cb2_fk_requireme` (`user_id`);

--
-- Indexes for table `requirements_app_user`
--
ALTER TABLE `requirements_app_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `requirements_app_user_groups`
--
ALTER TABLE `requirements_app_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `requirements_app_user_groups_user_id_group_id_46df4382_uniq` (`user_id`,`group_id`),
  ADD KEY `requirements_app_user_groups_group_id_e937957a_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `requirements_app_user_user_permissions`
--
ALTER TABLE `requirements_app_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `requirements_app_user_us_user_id_permission_id_111abf26_uniq` (`user_id`,`permission_id`),
  ADD KEY `requirements_app_use_permission_id_af8368b0_fk_auth_perm` (`permission_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `requirements_app_formquestion`
--
ALTER TABLE `requirements_app_formquestion`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `requirements_app_formresponse`
--
ALTER TABLE `requirements_app_formresponse`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `requirements_app_formsection`
--
ALTER TABLE `requirements_app_formsection`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `requirements_app_questionresponse`
--
ALTER TABLE `requirements_app_questionresponse`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `requirements_app_requirementform`
--
ALTER TABLE `requirements_app_requirementform`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `requirements_app_user`
--
ALTER TABLE `requirements_app_user`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `requirements_app_user_groups`
--
ALTER TABLE `requirements_app_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `requirements_app_user_user_permissions`
--
ALTER TABLE `requirements_app_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_requirements_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `requirements_app_user` (`id`);

--
-- Constraints for table `requirements_app_formquestion`
--
ALTER TABLE `requirements_app_formquestion`
  ADD CONSTRAINT `requirements_app_for_section_id_77b7f781_fk_requireme` FOREIGN KEY (`section_id`) REFERENCES `requirements_app_formsection` (`id`);

--
-- Constraints for table `requirements_app_formresponse`
--
ALTER TABLE `requirements_app_formresponse`
  ADD CONSTRAINT `requirements_app_for_form_id_617f265d_fk_requireme` FOREIGN KEY (`form_id`) REFERENCES `requirements_app_requirementform` (`id`),
  ADD CONSTRAINT `requirements_app_for_question_id_92dbb5ff_fk_requireme` FOREIGN KEY (`question_id`) REFERENCES `requirements_app_formquestion` (`id`);

--
-- Constraints for table `requirements_app_questionresponse`
--
ALTER TABLE `requirements_app_questionresponse`
  ADD CONSTRAINT `requirements_app_que_form_id_91bd3f74_fk_requireme` FOREIGN KEY (`form_id`) REFERENCES `requirements_app_requirementform` (`id`),
  ADD CONSTRAINT `requirements_app_que_question_id_c5bfc83f_fk_requireme` FOREIGN KEY (`question_id`) REFERENCES `requirements_app_formquestion` (`id`);

--
-- Constraints for table `requirements_app_requirementform`
--
ALTER TABLE `requirements_app_requirementform`
  ADD CONSTRAINT `requirements_app_req_user_id_c66d5cb2_fk_requireme` FOREIGN KEY (`user_id`) REFERENCES `requirements_app_user` (`id`);

--
-- Constraints for table `requirements_app_user_groups`
--
ALTER TABLE `requirements_app_user_groups`
  ADD CONSTRAINT `requirements_app_use_user_id_85bf74d2_fk_requireme` FOREIGN KEY (`user_id`) REFERENCES `requirements_app_user` (`id`),
  ADD CONSTRAINT `requirements_app_user_groups_group_id_e937957a_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `requirements_app_user_user_permissions`
--
ALTER TABLE `requirements_app_user_user_permissions`
  ADD CONSTRAINT `requirements_app_use_permission_id_af8368b0_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `requirements_app_use_user_id_c6cb62d5_fk_requireme` FOREIGN KEY (`user_id`) REFERENCES `requirements_app_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
