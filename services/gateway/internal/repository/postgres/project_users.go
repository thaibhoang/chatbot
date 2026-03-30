package postgres

import (
	"context"
	"database/sql"
)

type ProjectUserRepository struct {
	db *sql.DB
}

func NewProjectUserRepository(db *sql.DB) *ProjectUserRepository {
	return &ProjectUserRepository{db: db}
}

func (r *ProjectUserRepository) CreateProjectUser(
	ctx context.Context,
	email string,
	passwordHash string,
	projectID string,
) (string, error) {
	var id string
	err := r.db.QueryRowContext(
		ctx,
		`INSERT INTO project_users(id, email, password_hash, project_id, status)
		 VALUES(gen_random_uuid(), $1, $2, $3::uuid, 'active')
		 RETURNING id::text`,
		email,
		passwordHash,
		projectID,
	).Scan(&id)
	return id, err
}
