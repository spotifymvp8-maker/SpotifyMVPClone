--
-- PostgreSQL database dump
--

\restrict cLp1viFFcxv3cJTTgDwLn9TIVbW9Uj1SGcT0Ns5amzfueSI9OAQSJ0NXvbNhWd2

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: albums; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.albums VALUES ('771f4cde-d239-421e-a388-f439cfd74319', 'Urban Nights', 'Various Artists', '/media/albums/1.jpg', 2024, '2026-03-06 12:23:01.312977+00', '2026-03-06 12:23:01.312977+00');
INSERT INTO public.albums VALUES ('afa7ea3a-37cf-42eb-96fb-d5b2549a86a2', 'Coastal Dreaming', 'Various Artists', '/media/albums/2.jpg', 2024, '2026-03-06 12:23:01.35023+00', '2026-03-06 12:23:01.35023+00');
INSERT INTO public.albums VALUES ('81b36d3c-4f6c-4ac2-8490-5cd1fe56ff4f', 'Midnight Sessions', 'Various Artists', '/media/albums/3.jpg', 2024, '2026-03-06 12:23:01.366768+00', '2026-03-06 12:23:01.366768+00');
INSERT INTO public.albums VALUES ('3593cbbd-629d-4f59-8b88-3e8b68aad18a', 'Eastern Dreams', 'Various Artists', '/media/albums/4.jpg', 2024, '2026-03-06 12:23:01.376565+00', '2026-03-06 12:23:01.376565+00');
INSERT INTO public.albums VALUES ('b809b911-d0b8-4ee9-a790-7a43988233a4', 'Nech', 'Sergey A.', '/media/images/ca37bd467a87486c8a3609f896beec1b.webp', 2026, '2026-03-13 18:58:47.792284+00', '2026-03-13 18:59:04.922306+00');


--
-- Data for Name: auth_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.auth_users VALUES ('0ec9467a-45a9-4477-a04e-4ea5fe5be301', 'Teslyar2008@gmail.com', 'd9648a56bbf74a83ae9266b225f3cbdfcf7b682fef0861a7610fdcf2a875213a', '2026-03-06 14:50:11.447954+00', NULL);
INSERT INTO public.auth_users VALUES ('c71f4c43-51bf-48ef-96b4-6b62375813af', 'test@example.com', '$2b$12$BMssP3bTAu3p941CE.BMt.Jc0ucLzJoWJPu/2hc7MA.OTnXP11x1O', '2026-03-06 12:23:01.1745+00', NULL);


--
-- Data for Name: tracks; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.tracks VALUES ('91bfc39f-c6c2-4b43-989e-71066a9315d7', 'Desert Wind', 'Sahara Sons', '', 28, '/media/songs/8.mp3', '2026-03-06 12:23:01.384283+00', NULL, '/media/cover-images/8.jpg', '2026-03-06 12:23:01.384283+00');
INSERT INTO public.tracks VALUES ('98795cf3-497d-46b4-8149-94fb68fdf08c', 'Winter Dreams', 'Arctic Pulse', '', 29, '/media/songs/11.mp3', '2026-03-06 12:23:01.384283+00', NULL, '/media/cover-images/11.jpg', '2026-03-06 12:23:01.384283+00');
INSERT INTO public.tracks VALUES ('495d2867-f85e-41c7-bdca-e71aea269d1b', 'Midnight Blues', 'Jazz Cats', '', 29, '/media/songs/18.mp3', '2026-03-06 12:23:01.384283+00', NULL, '/media/cover-images/18.jpg', '2026-03-06 12:23:01.384283+00');
INSERT INTO public.tracks VALUES ('0de82c16-043b-4c3e-982c-666392ab2214', 'Neon Dreams', 'Cyber Pulse', 'Urban Nights', 267, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-13.mp3', '2026-03-06 12:23:01.35023+00', 'afa7ea3a-37cf-42eb-96fb-d5b2549a86a2', 'https://picsum.photos/seed/t13/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('12453cfd-ed23-44cf-9f51-45b5d1707bbf', 'Moonlight Dance', 'Silver Shadows', 'Midnight Sessions', 201, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3', '2026-03-06 12:23:01.384283+00', NULL, 'https://picsum.photos/seed/t12/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('16586542-9649-4d40-8e8e-426184b0627a', 'Neon Tokyo', 'Future Pulse', 'Eastern Dreams', 178, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3', '2026-03-06 12:23:01.384283+00', NULL, 'https://picsum.photos/seed/t8/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('1ac51b7d-fab6-4eae-9c35-04fb346a179a', 'Midnight Drive', 'The Wanderers', 'Midnight Sessions', 198, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3', '2026-03-06 12:23:01.376565+00', '3593cbbd-629d-4f59-8b88-3e8b68aad18a', 'https://picsum.photos/seed/t2/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('2b07c750-d2d4-40af-8198-0ce784b41e1b', 'City Rain', 'Urban Echo', 'Urban Nights', 245, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3', '2026-03-06 12:23:01.312977+00', '771f4cde-d239-421e-a388-f439cfd74319', 'https://picsum.photos/seed/t7/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('4e8f18b3-a472-494a-968c-5e528ad1b4ad', 'Midnight Drive', 'The Wanderers', 'Midnight Sessions', 189, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-17.mp3', '2026-03-06 12:23:01.384283+00', NULL, 'https://picsum.photos/seed/t17/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('500473ab-3323-4004-b307-5f1ff10c7d3d', 'Lost in Tokyo', 'Electric Dreams', 'Eastern Dreams', 214, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3', '2026-03-06 12:23:01.384283+00', NULL, 'https://picsum.photos/seed/t6/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('51f6d288-c098-4125-a89f-22a015e62ca4', 'Neon Lights', 'Night Runners', 'Urban Nights', 198, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3', '2026-03-06 12:23:01.312977+00', '771f4cde-d239-421e-a388-f439cfd74319', 'https://picsum.photos/seed/t5/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('6d141b4b-f69f-4678-97f8-98514c8febf9', 'Ocean Waves', 'Coastal Drift', 'Coastal Dreaming', 214, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3', '2026-03-06 12:23:01.35023+00', 'afa7ea3a-37cf-42eb-96fb-d5b2549a86a2', 'https://picsum.photos/seed/t9/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('91dbd9f6-b162-4e30-83e5-7177fe9c15dc', 'Lost in Tokyo', 'Electric Dreams', 'Eastern Dreams', 178, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3', '2026-03-06 12:23:01.376565+00', '3593cbbd-629d-4f59-8b88-3e8b68aad18a', 'https://picsum.photos/seed/t3/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('98dc5601-f63d-43f4-a5b4-181685c6bd82', 'Moonlight Dance', 'Silver Shadows', 'Midnight Sessions', 223, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-14.mp3', '2026-03-06 12:23:01.376565+00', '3593cbbd-629d-4f59-8b88-3e8b68aad18a', 'https://picsum.photos/seed/t14/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('a471b815-3d43-47bd-a5a1-2b43f6f47b32', 'Urban Jungle', 'City Lights', 'Urban Nights', 223, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3', '2026-03-06 12:23:01.312977+00', '771f4cde-d239-421e-a388-f439cfd74319', 'https://picsum.photos/seed/t15/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('aad115d4-a422-4aa2-8579-5f43f319d7eb', 'Mountain High', 'The Wild Ones', '', 189, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-18.mp3', '2026-03-06 12:23:01.384283+00', NULL, 'https://picsum.photos/seed/t18/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('be15b32b-49e1-4b81-95eb-601b76ec41d4', 'Purple Sunset', 'Dream Valley', 'Eastern Dreams', 195, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3', '2026-03-06 12:23:01.384283+00', NULL, 'https://picsum.photos/seed/t11/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('c602c3c0-3c25-4c71-a847-b75be443e248', 'Crystal Rain', 'Echo Valley', 'Coastal Dreaming', 243, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-16.mp3', '2026-03-06 12:23:01.366768+00', '81b36d3c-4f6c-4ac2-8490-5cd1fe56ff4f', 'https://picsum.photos/seed/t16/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('e14d3341-a08d-4ee0-bfbd-ddeb07417298', 'Starlight', 'Luna Bay', 'Coastal Dreaming', 195, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3', '2026-03-06 12:23:01.366768+00', '81b36d3c-4f6c-4ac2-8490-5cd1fe56ff4f', 'https://picsum.photos/seed/t10/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('ef422f97-75d9-4436-ac78-73848e5cb8dc', 'Summer Daze', 'Coastal Kids', 'Coastal Dreaming', 187, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3', '2026-03-06 12:23:01.35023+00', 'afa7ea3a-37cf-42eb-96fb-d5b2549a86a2', 'https://picsum.photos/seed/t4/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('fa2e520c-f462-4172-b043-b3c6b6935e42', 'Stay With Me', 'Sarah Mitchell', 'Midnight Sessions', 245, 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', '2026-03-06 12:23:01.366768+00', '81b36d3c-4f6c-4ac2-8490-5cd1fe56ff4f', 'https://picsum.photos/seed/t1/300/300', '2026-03-06 17:55:12.724068+00');
INSERT INTO public.tracks VALUES ('ea2daf13-6df4-447c-ab98-c1d522561f1d', 'Nech', 'Sergey A.', 'Nech', 201, '/media/songs/2259cc69c6214753a41f9d60723f9357.mp3', '2026-03-13 18:59:52.560639+00', 'b809b911-d0b8-4ee9-a790-7a43988233a4', '/media/images/164abfc65b8848fcbfa851705d62322d.webp', '2026-03-13 18:59:52.560639+00');
INSERT INTO public.tracks VALUES ('a4dba17b-287f-46a3-97fd-8c2f105d3534', 'Теща', 'Sergey A.', 'Nech', 247, '/media/songs/989f36702242440588ae7a6117ce7fd4.mp3', '2026-03-13 19:00:46.675076+00', 'b809b911-d0b8-4ee9-a790-7a43988233a4', '/media/images/7f39d9ae1fc54688b8e0a486981dfa90.webp', '2026-03-13 19:00:46.675076+00');


--
-- Data for Name: user_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.user_profiles VALUES ('c71f4c43-51bf-48ef-96b4-6b62375813af', 'testuser', 'https://picsum.photos/seed/user/200/200', 'Test user account', '2026-03-06 12:23:01.1745+00', '2026-03-06 12:23:01.1745+00');
INSERT INTO public.user_profiles VALUES ('0ec9467a-45a9-4477-a04e-4ea5fe5be301', 'Teslyar2008@gmail.com', NULL, '', '2026-03-06 14:50:11.447954+00', '2026-03-06 14:50:11.447954+00');


--
-- PostgreSQL database dump complete
--

\unrestrict cLp1viFFcxv3cJTTgDwLn9TIVbW9Uj1SGcT0Ns5amzfueSI9OAQSJ0NXvbNhWd2

