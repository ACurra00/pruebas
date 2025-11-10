--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1
-- Dumped by pg_dump version 15.1

-- Started on 2023-06-28 11:49:30

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 214 (class 1259 OID 16493)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    name character varying,
    ci character varying NOT NULL,
    apellidos character varying,
    ocupacion character varying,
    resumen_rol character varying,
    correo character varying,
    consejo character varying
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 3316 (class 0 OID 16493)
-- Dependencies: 214
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (name, ci, apellidos, ocupacion, resumen_rol, correo, consejo) FROM stdin;
Martha	00000000001	Delgado Dapena	Vicerrectora Primera	Consejo	vicerrectora.primera@tesla.cujae.edu.cu	x
Anaisa	00000000002	Hernandez Gonzalez	Vicerrectora Docente	Consejo	vrd@tesla.cujae.edu.cu	x
Daniel	00000000003	Alfonso Robaina	Vicerrector de Investigacion y Postgrado	Consejo	vrip@tesla.cujae.edu.cu	x
Diego	00000000004	 Fernandez Labrada	Vicerrector de Extension Universitaria	Consejo	vreu@tesla.cujae.edu.cu	x
Dianelys	00000000005	Amaro Martinez	Director General de Economia	Consejo	dge@tesla.cuaje.edu.cu	x
Yoimi	00000000006	Trujillo Reyna	Director General de Logistica	Consejo	logistica@tesla	x
Esther	00000000007	Ansola Hazday	Secretaria General	Cuadro	sec.general@tesla.cujae.edu.cu	\N
Marcos Antonio	00000000008	Bannos Martinez	Director de Calidad	Consejo	dir.calidad@tesla.cujae.edu.cu	x
Eugenio	00000000009	Carlos Rodriguez	Director de Calidad	Consejo	cuadros@tesla.cujae.edu.cu	x
Luis Alberto	00000000010	Rueda	Director de Relaciones Internacionales	Consejo	dri@tesla.cujae.edu.cu	x
Reyniel	00000000011	Gomez Gonzalez	Director de Recursos Humanos	Consejo	dcrh@tesla.cujae.edu.cu	x
Yoiselen	00000000012	Casanave Macias	Decano de la Facultad de Arquitectura	Consejo	decano.arquitectura@tesla.cujae.edu.cu	x
Odalys	64101002296	Alvarez Rodriguez	Decana de la Facultad de Ingenieria Civil	Consejo	decano.civil@tesla.cujae.edu.cu	x
Tania	69030800772	Carbonell	Decano de la Facultad de Ingenieria Quimica	Consejo	decano.quimica@tesla.cujae.edu.cu	x
Deny	69102010108	Oliva Merencio	Decano de la Facultad de Ingenieria Mecanica	Consejo	decano.mecanica@tesla.cujae.edu.cu	x
Modesto Ricardo	70120611488	Gomez Crespo	Rector	Consejo	rectorado@tesla.cujae.edu.cu	x
Raisa	72050901014	Socorro Llanes	Decano de la Facultad de Ingenieria Informatica	Consejo	decano.informatica@tesla.cujae.edu.cu	x
Yadary	76112141075	Ortega Gonzalez	Decano de la Facultad de Industrial	Consejo	decano.industrial@tesla.cujae.edu.cu	x
Humberto	80092607729	Diaz Pando	Director General Informacion, Comunicacion e Informatizacion	Consejo	vric@tesla.cujae.edu.cu	x
Ariel	83120627264	Santos Fuentefrias	Decano de la Facultad de  Ingenieria Electrica	Consejo	decano.electrica@tesla.cujae.edu.cu	x
Adrian	87091906686	Rodriguez Ramos	Decano de la Facultad Automatica y Biomedica	Consejo	decano.automatica@tesla.cujae.edu.cu	x
Pedro G	12345678902	Alfonso Leonard	Director de Historia yMarx- Len\n	Consejo	\N	x
Tania	12345678901	Rodriguez Moliner	Directora del Citi	Consejo	.	x
Carlos	00000000013	Figueroa Hernandez	Jefe de Despacho	Cuadro	rectorado@tesla.cujae.edu.cu	\N
Manuel	60102911264	De la Rua	Director General del Instituto de Ciencias Basicas	Consejo	director.icb@tesla.cujae.edu.cu	x
Mario	63102600886	Martinez Lopez	Secretario General del Partido	Cuadro	pcc@tesla.cujae.edu.cu	\N
Pablo	73051609169	Montejo Valdes	Decano de la Facultad de Telecomunicaciones y Electronica	Consejo	decano.tele@tesla.cujae.edu.cu	x
Indira	87122009159	Ordonnez Reyes	Secretario General del Sindicato	Cuadro	ctc@tesla.cujae.edu.cu	\N
Andres	98012108648	Carvajal Elena	Presidente de la FEU	Cuadro	feu@tesla.cujae.edu.cu	\N
Diansy	98031408219	Rodriguez Hong	Secretario General de la UJC	Cuadro	ujc@tesla.cujae.	\N
\.


--
-- TOC entry 3173 (class 2606 OID 16499)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (ci);


-- Completed on 2023-06-28 11:49:30

--
-- PostgreSQL database dump complete
--

