--
-- PostgreSQL database dump
--

-- Dumped from database version 17.3 (Debian 17.3-1.pgdg120+1)
-- Dumped by pg_dump version 17.2

-- Started on 2025-12-19 08:40:34

--
-- TOC entry 220 (class 1259 OID 24577)
-- Name: conferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conferences (
    conference_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    short_description character varying(500) NOT NULL,
    full_description text,
    start_date date NOT NULL,
    end_date date NOT NULL,
    registration_deadline date,
    location character varying(255) NOT NULL,
    max_participants integer,
    status character varying(9) NOT NULL,
    organizer_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.conferences OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16390)
-- Name: identities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.identities (
    identity_id uuid NOT NULL,
    username character varying NOT NULL,
    password character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.identities OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 24586)
-- Name: participants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.participants (
    user_id uuid NOT NULL,
    username character varying(255) NOT NULL,
    surname character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    patronymic character varying(255),
    phone_number character varying(20) NOT NULL,
    home_number character varying(20),
    academic_degree character varying(9),
    academic_title character varying(9),
    research_area character varying(16),
    organization character varying(255),
    department character varying(255),
    "position" character varying(255),
    country character varying(255) NOT NULL,
    city character varying(255) NOT NULL,
    postal_code character varying(20),
    street_address character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.participants OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 24597)
-- Name: participations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.participations (
    conference_id uuid NOT NULL,
    participant_id uuid NOT NULL,
    role character varying(11) NOT NULL,
    first_invitation_date date,
    application_date date,
    submission_topic character varying(500),
    submission_thesis_received boolean,
    second_invitation_date date,
    fee_payment_date date,
    fee_amount double precision,
    fee_currency character varying(3),
    arrival_date date,
    departure_date date,
    needs_hotel boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.participations OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16401)
-- Name: tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tokens (
    token_id uuid NOT NULL,
    identity_id uuid NOT NULL,
    value character varying NOT NULL,
    issued_at timestamp with time zone NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    revoked boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tokens OWNER TO postgres;

--
-- TOC entry 3240 (class 2606 OID 16389)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 3250 (class 2606 OID 24585)
-- Name: conferences conferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conferences
    ADD CONSTRAINT conferences_pkey PRIMARY KEY (conference_id);


--
-- TOC entry 3242 (class 2606 OID 16398)
-- Name: identities identities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.identities
    ADD CONSTRAINT identities_pkey PRIMARY KEY (identity_id);


--
-- TOC entry 3244 (class 2606 OID 16400)
-- Name: identities identities_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.identities
    ADD CONSTRAINT identities_username_key UNIQUE (username);


--
-- TOC entry 3252 (class 2606 OID 24594)
-- Name: participants participants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.participants
    ADD CONSTRAINT participants_pkey PRIMARY KEY (user_id);


--
-- TOC entry 3254 (class 2606 OID 24596)
-- Name: participants participants_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.participants
    ADD CONSTRAINT participants_username_key UNIQUE (username);


--
-- TOC entry 3256 (class 2606 OID 24605)
-- Name: participations participations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.participations
    ADD CONSTRAINT participations_pkey PRIMARY KEY (conference_id, participant_id);


--
-- TOC entry 3246 (class 2606 OID 16409)
-- Name: tokens tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT tokens_pkey PRIMARY KEY (token_id);


--
-- TOC entry 3248 (class 2606 OID 16411)
-- Name: tokens tokens_value_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT tokens_value_key UNIQUE (value);


--
-- TOC entry 3257 (class 2606 OID 24606)
-- Name: participations participations_conference_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.participations
    ADD CONSTRAINT participations_conference_id_fkey FOREIGN KEY (conference_id) REFERENCES public.conferences(conference_id) ON DELETE CASCADE;


-- Completed on 2025-12-19 08:40:34

--
-- PostgreSQL database dump complete
--

--
-- Manual updates
--

ALTER TABLE ONLY public.participations
    ADD COLUMN IF NOT EXISTS revoked BOOLEAN;