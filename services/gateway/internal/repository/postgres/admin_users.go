package postgres

import (
	"context"
	"database/sql"
	"errors"
)

var ErrInvalidAdminCredential = errors.New("invalid admin credential")

type AdminRepository struct {
	db *sql.DB
}

func NewAdminRepository(db *sql.DB) *AdminRepository {
	return &AdminRepository{db: db}
}

func (r *AdminRepository) CreateAdminUser(ctx context.Context, email, passwordHash string) (string, error) {
	var id string
	err := r.db.QueryRowContext(
		ctx,
		`INSERT INTO admin_users(id, email, password_hash, status)
		 VALUES(gen_random_uuid(), $1, $2, 'active')
		 RETURNING id::text`,
		email,
		passwordHash,
	).Scan(&id)
	return id, err
}

func (r *AdminRepository) GetAdminHashByEmail(ctx context.Context, email string) (string, string, error) {
	var (
		id   string
		hash string
	)
	err := r.db.QueryRowContext(
		ctx,
		`SELECT id::text, password_hash FROM admin_users WHERE email = $1 AND status = 'active'`,
		email,
	).Scan(&id, &hash)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return "", "", ErrInvalidAdminCredential
		}
		return "", "", err
	}
	return id, hash, nil
}

func (r *AdminRepository) CountAdmins(ctx context.Context) (int, error) {
	var c int
	if err := r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM admin_users`).Scan(&c); err != nil {
		return 0, err
	}
	return c, nil
}
