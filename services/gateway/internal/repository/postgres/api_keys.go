package postgres

import (
	"context"
	"database/sql"
	"errors"

	"golang.org/x/crypto/bcrypt"
)

var ErrInvalidAccessKey = errors.New("invalid access key")

type APIKeyRepository struct {
	db *sql.DB
}

func NewAPIKeyRepository(db *sql.DB) *APIKeyRepository {
	return &APIKeyRepository{db: db}
}

func (r *APIKeyRepository) CreateAccessKey(
	ctx context.Context,
	projectID string,
	accessKeyID string,
	secretHash string,
	description string,
) error {
	_, err := r.db.ExecContext(
		ctx,
		`INSERT INTO api_keys(id, project_id, access_key_id, access_key_secret_hash, description)
		 VALUES(gen_random_uuid(), $1::uuid, $2, $3, $4)`,
		projectID,
		accessKeyID,
		secretHash,
		description,
	)
	return err
}

func (r *APIKeyRepository) VerifyAccessKey(ctx context.Context, accessKeyID, secret string) (string, error) {
	var (
		projectID  string
		secretHash string
	)
	err := r.db.QueryRowContext(
		ctx,
		`SELECT project_id::text, access_key_secret_hash FROM api_keys WHERE access_key_id = $1`,
		accessKeyID,
	).Scan(&projectID, &secretHash)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return "", ErrInvalidAccessKey
		}
		return "", err
	}

	if err := bcrypt.CompareHashAndPassword([]byte(secretHash), []byte(secret)); err != nil {
		return "", ErrInvalidAccessKey
	}
	_, _ = r.db.ExecContext(ctx, `UPDATE api_keys SET last_used = NOW() WHERE access_key_id = $1`, accessKeyID)
	return projectID, nil
}
