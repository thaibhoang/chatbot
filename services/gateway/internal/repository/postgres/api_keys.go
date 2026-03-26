package postgres

import "context"

type APIKeyRepository struct{}

func NewAPIKeyRepository() *APIKeyRepository {
	return &APIKeyRepository{}
}

func (r *APIKeyRepository) VerifyAccessKey(ctx context.Context, accessKeyID, secret string) (string, error) {
	_ = ctx
	_ = accessKeyID
	_ = secret
	// TODO: load hash from postgres and verify.
	return "stub-project", nil
}
