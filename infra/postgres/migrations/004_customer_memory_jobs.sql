CREATE TABLE IF NOT EXISTS customer_memory_states (
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  customer_id TEXT NOT NULL,
  unsummarized_messages INT NOT NULL DEFAULT 0,
  unsummarized_tokens INT NOT NULL DEFAULT 0,
  has_signal BOOLEAN NOT NULL DEFAULT FALSE,
  last_enqueued_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY(project_id, customer_id)
);

CREATE TABLE IF NOT EXISTS customer_memory_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  customer_id TEXT NOT NULL,
  source_window_id TEXT NOT NULL,
  payload JSONB NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'done', 'dead')) DEFAULT 'pending',
  attempts INT NOT NULL DEFAULT 0,
  max_attempts INT NOT NULL DEFAULT 5,
  last_error TEXT,
  run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(project_id, customer_id, source_window_id)
);

CREATE INDEX IF NOT EXISTS idx_customer_memory_jobs_status_run_at
ON customer_memory_jobs(status, run_at);
