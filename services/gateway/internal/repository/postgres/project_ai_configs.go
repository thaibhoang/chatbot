package postgres

import (
	"context"
	"database/sql"
	"errors"
)

var ErrProjectAIConfigNotFound = errors.New("project ai config not found")

type ProjectAIConfig struct {
	ProjectID       string
	Provider        string
	Model           string
	APIKeyEncrypted string
	Status          string
}

type ProjectAIConfigRepository struct {
	db *sql.DB
}

func NewProjectAIConfigRepository(db *sql.DB) *ProjectAIConfigRepository {
	return &ProjectAIConfigRepository{db: db}
}

func (r *ProjectAIConfigRepository) UpsertActiveConfig(
	ctx context.Context,
	projectID, provider, model, apiKeyEncrypted string,
) error {
	_, err := r.db.ExecContext(
		ctx,
		`INSERT INTO project_ai_configs(project_id, provider, model, api_key_encrypted, status, updated_at)
		 VALUES($1::uuid, $2, $3, $4, 'active', NOW())
		 ON CONFLICT (project_id) WHERE status = 'active'
		 DO UPDATE SET provider = EXCLUDED.provider,
		               model = EXCLUDED.model,
		               api_key_encrypted = EXCLUDED.api_key_encrypted,
		               status = 'active',
		               updated_at = NOW()`,
		projectID,
		provider,
		model,
		apiKeyEncrypted,
	)
	return err
}

func (r *ProjectAIConfigRepository) GetActiveConfig(ctx context.Context, projectID string) (*ProjectAIConfig, error) {
	var out ProjectAIConfig
	err := r.db.QueryRowContext(
		ctx,
		`SELECT project_id::text, provider, model, api_key_encrypted, status
		 FROM project_ai_configs
		 WHERE project_id = $1::uuid AND status = 'active'
		 LIMIT 1`,
		projectID,
	).Scan(&out.ProjectID, &out.Provider, &out.Model, &out.APIKeyEncrypted, &out.Status)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrProjectAIConfigNotFound
		}
		return nil, err
	}
	return &out, nil
}
