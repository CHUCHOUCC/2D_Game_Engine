-- One learning step: what the model saw after a run and the reward it got.
create table if not exists ai_training_samples (
    id              bigint generated always as identity primary key,
    ai_model_id     bigint      not null references ai_models (id) on delete cascade,
    play_session_id bigint      references play_sessions (id) on delete set null,
    features        jsonb       not null,
    reward          real        not null,
    created_at      timestamptz not null default now()
);
