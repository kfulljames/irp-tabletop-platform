-- ============================================================================
-- IRP Tabletop Platform — Supabase schema (productized model)
-- Ports the local SQLite prototype (app/irp/db.py) to Postgres and adds the
-- things the prototype skipped per decision B0: real auth, multi-tenant orgs,
-- and Row-Level Security. A "tenant"/"client" here = the MSP's customer being
-- exercised; a "facilitator" = a the MSP staff member (auth user) who can work
-- across many client orgs.
--
-- Run this in the Supabase SQL editor. Safe to run once on a fresh project.
-- ============================================================================

-- ---- Facilitator accounts (mirror of auth.users) --------------------------
create table if not exists profile (
  id          uuid primary key references auth.users(id) on delete cascade,
  full_name   text,
  created_at  timestamptz not null default now()
);

-- ---- Workspace = the the MSP tenant (white-label owner) -------------------
-- One workspace per MSP. Facilitators belong to a workspace; client_orgs live
-- under it. (For a single-MSP launch you'll have exactly one workspace row.)
create table if not exists workspace (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  created_at  timestamptz not null default now()
);

create table if not exists workspace_member (
  workspace_id uuid not null references workspace(id) on delete cascade,
  profile_id   uuid not null references profile(id)   on delete cascade,
  role         text not null default 'facilitator',   -- owner | facilitator
  primary key (workspace_id, profile_id)
);

-- ---- Client org = the customer being exercised (the "tenant" guardrail) ---
create table if not exists client_org (
  id           uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspace(id) on delete cascade,
  name         text not null,
  industry     text,
  created_at   timestamptz not null default now()
);

-- ---- Plan corpus: a client can have many docs (policy + procedure, IRP+BCP)
create table if not exists document (
  id              uuid primary key default gen_random_uuid(),
  client_org_id   uuid not null references client_org(id) on delete cascade,
  label           text,                 -- 'Policy' | 'Procedure' | 'IRP' | 'BCP'
  source_filename text,
  full_text       text,                 -- extracted text (edge fn fills this)
  uploaded_at     timestamptz not null default now()
);

-- ---- Plan mapped onto canonical baseline chapters (replaced per analysis run)
create table if not exists plan_section (
  id            uuid primary key default gen_random_uuid(),
  client_org_id uuid not null references client_org(id) on delete cascade,
  baseline_key  text not null,
  title         text not null,
  original_text text
);

-- ---- Gap findings: AI-suggested + room-validated punch-list ----------------
create table if not exists gap_finding (
  id                 uuid primary key default gen_random_uuid(),
  client_org_id      uuid not null references client_org(id) on delete cascade,
  baseline_key       text,
  title              text not null,
  description        text,
  recommended_change text,
  severity           text not null default 'medium',        -- none|low|medium|high
  status             text not null default 'ai_suggested',  -- ai_suggested|validated|dismissed
  source             text not null default 'ai',            -- ai|room
  created_at         timestamptz not null default now()
);

-- ---- People roster (real participants; used for act-as attribution) --------
create table if not exists person (
  id            uuid primary key default gen_random_uuid(),
  client_org_id uuid not null references client_org(id) on delete cascade,
  full_name     text not null,
  title         text,
  incident_role text,
  created_at    timestamptz not null default now()
);

-- ---- Scenario library (was scenarios.py). Global/seeded, optionally per-ws -
create table if not exists scenario (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid references workspace(id) on delete cascade,  -- null = global seed
  key           text not null,
  title         text not null,
  summary       text,
  summary_title text,
  summary_fields jsonb not null default '[]',   -- [[fkey,flabel,kind], ...]
  created_at    timestamptz not null default now()
);

create table if not exists inject (
  id          uuid primary key default gen_random_uuid(),
  scenario_id uuid not null references scenario(id) on delete cascade,
  ord         int not null,                 -- linear reveal order
  title       text not null,
  category    text,                         -- Detection|Escalation|Decision|Comms|Containment|Legal|Recovery
  room        text,                         -- read/shown to the room
  guidance    text                          -- facilitator-only teleprompter
);

create table if not exists scenario_task (
  id          uuid primary key default gen_random_uuid(),
  scenario_id uuid not null references scenario(id) on delete cascade,
  phase       text,
  title       text not null,
  ord         int not null default 0
);

-- ---- A live exercise/session ----------------------------------------------
create table if not exists run (
  id             uuid primary key default gen_random_uuid(),
  client_org_id  uuid not null references client_org(id) on delete cascade,
  scenario_id    uuid references scenario(id),
  scenario_key   text not null,
  scenario_title text,
  status         text not null default 'running',  -- running|complete
  current_inject int not null default 0,
  timezone       text,                              -- IANA tz; all run timestamps use it
  started_at     timestamptz,
  resolved_at    timestamptz,
  -- report-only structured fields live here as jsonb instead of the prototype's
  -- run_kv table: impact ratings, per-type summary, debrief, closing_notes, report_status
  meta           jsonb not null default '{}',
  created_at     timestamptz not null default now()
);

create table if not exists run_participant (
  id        uuid primary key default gen_random_uuid(),
  run_id    uuid not null references run(id)    on delete cascade,
  person_id uuid not null references person(id) on delete cascade,
  role      text not null default 'participant'  -- participant|observer
);

create table if not exists run_overview (
  run_id            uuid primary key references run(id) on delete cascade,
  latest_status     text,
  detection_summary text,
  how_discovered    text,
  when_discovered   text,
  who_discovered    text,
  impacted          text,
  history           text,
  updated_at        timestamptz
);

create table if not exists run_task (
  id       uuid primary key default gen_random_uuid(),
  run_id   uuid not null references run(id) on delete cascade,
  phase    text,
  title    text not null,
  assignee text,
  status   text not null default 'pending',  -- pending|done
  ord      int not null default 0
);

create table if not exists run_vote (
  id           uuid primary key default gen_random_uuid(),
  run_id       uuid not null references run(id)    on delete cascade,
  person_id    uuid references person(id) on delete set null,
  score        int,                              -- 1-10 EOS-style
  submitted_at timestamptz
);

create table if not exists timeline_event (
  id               uuid primary key default gen_random_uuid(),
  run_id           uuid not null references run(id) on delete cascade,
  occurred_at      timestamptz not null,
  type             text not null,                -- Business decision|Comms decision|Task|Status update|Note / plan gap|Inject|Incident start|Resolution
  acting_person_id uuid references person(id) on delete set null,
  description      text,
  payload          jsonb,
  created_at       timestamptz not null default now()
);

-- ============================================================================
-- Row-Level Security: a facilitator sees only data under workspaces they belong
-- to. client_org is the hinge; everything else joins back to it (or to workspace).
-- ============================================================================
alter table profile          enable row level security;
alter table workspace        enable row level security;
alter table workspace_member enable row level security;
alter table client_org       enable row level security;
alter table document         enable row level security;
alter table plan_section     enable row level security;
alter table gap_finding      enable row level security;
alter table person           enable row level security;
alter table scenario         enable row level security;
alter table inject           enable row level security;
alter table scenario_task    enable row level security;
alter table run              enable row level security;
alter table run_participant  enable row level security;
alter table run_overview     enable row level security;
alter table run_task         enable row level security;
alter table run_vote         enable row level security;
alter table timeline_event   enable row level security;

-- helper: is the current user a member of a given workspace?
create or replace function is_ws_member(ws uuid)
returns boolean language sql security definer stable as $$
  select exists (
    select 1 from workspace_member m
    where m.workspace_id = ws and m.profile_id = auth.uid()
  );
$$;

-- helper: workspace that owns a given client_org
create or replace function ws_of_client(c uuid)
returns uuid language sql security definer stable as $$
  select workspace_id from client_org where id = c;
$$;

-- profile: a user sees/edits only their own row
create policy profile_self on profile
  for all using (id = auth.uid()) with check (id = auth.uid());

-- workspace + membership
create policy ws_member_read on workspace
  for select using (is_ws_member(id));
create policy wsm_self on workspace_member
  for select using (profile_id = auth.uid() or is_ws_member(workspace_id));

-- client_org: scoped to member workspaces
create policy client_org_rw on client_org
  for all using (is_ws_member(workspace_id))
  with check (is_ws_member(workspace_id));

-- everything hung off client_org
create policy document_rw on document
  for all using (is_ws_member(ws_of_client(client_org_id)))
  with check (is_ws_member(ws_of_client(client_org_id)));
create policy plan_section_rw on plan_section
  for all using (is_ws_member(ws_of_client(client_org_id)))
  with check (is_ws_member(ws_of_client(client_org_id)));
create policy gap_finding_rw on gap_finding
  for all using (is_ws_member(ws_of_client(client_org_id)))
  with check (is_ws_member(ws_of_client(client_org_id)));
create policy person_rw on person
  for all using (is_ws_member(ws_of_client(client_org_id)))
  with check (is_ws_member(ws_of_client(client_org_id)));

-- scenario library: global seeds readable by all; workspace-owned scoped to members
create policy scenario_read on scenario
  for select using (workspace_id is null or is_ws_member(workspace_id));
create policy inject_read on inject
  for select using (exists (select 1 from scenario s where s.id = scenario_id
                            and (s.workspace_id is null or is_ws_member(s.workspace_id))));
create policy scenario_task_read on scenario_task
  for select using (exists (select 1 from scenario s where s.id = scenario_id
                            and (s.workspace_id is null or is_ws_member(s.workspace_id))));

-- runs + children: scope through run -> client_org -> workspace
create policy run_rw on run
  for all using (is_ws_member(ws_of_client(client_org_id)))
  with check (is_ws_member(ws_of_client(client_org_id)));

-- child tables of run share one shape: member of the run's workspace
create policy run_participant_rw on run_participant for all
  using (exists (select 1 from run r where r.id = run_id and is_ws_member(ws_of_client(r.client_org_id))))
  with check (exists (select 1 from run r where r.id = run_id and is_ws_member(ws_of_client(r.client_org_id))));
create policy run_overview_rw on run_overview for all
  using (exists (select 1 from run r where r.id = run_id and is_ws_member(ws_of_client(r.client_org_id))))
  with check (exists (select 1 from run r where r.id = run_id and is_ws_member(ws_of_client(r.client_org_id))));
create policy run_task_rw on run_task for all
  using (exists (select 1 from run r where r.id = run_id and is_ws_member(ws_of_client(r.client_org_id))))
  with check (exists (select 1 from run r where r.id = run_id and is_ws_member(ws_of_client(r.client_org_id))));
create policy run_vote_rw on run_vote for all
  using (exists (select 1 from run r where r.id = run_id and is_ws_member(ws_of_client(r.client_org_id))))
  with check (exists (select 1 from run r where r.id = run_id and is_ws_member(ws_of_client(r.client_org_id))));
create policy timeline_event_rw on timeline_event for all
  using (exists (select 1 from run r where r.id = run_id and is_ws_member(ws_of_client(r.client_org_id))))
  with check (exists (select 1 from run r where r.id = run_id and is_ws_member(ws_of_client(r.client_org_id))));

-- ---- new-user bootstrap: create profile row on signup --------------------
create or replace function handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into profile (id, full_name)
  values (new.id, coalesce(new.raw_user_meta_data->>'full_name', new.email))
  on conflict (id) do nothing;
  return new;
end; $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();
