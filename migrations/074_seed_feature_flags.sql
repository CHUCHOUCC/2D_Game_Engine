insert into feature_flags (code, enabled, description) values
    ('ai-learning',    true,  'The AI adapts obstacles to how players perform'),
    ('project-clone',  true,  'Users can duplicate a project'),
    ('leaderboards',   true,  'Show high scores per level')
on conflict (code) do nothing;
