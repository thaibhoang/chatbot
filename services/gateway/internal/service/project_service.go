package service

import "context"

type ProjectService struct{}

func NewProjectService() *ProjectService {
	return &ProjectService{}
}

func (s *ProjectService) CanUseQuota(ctx context.Context, projectID string) (bool, error) {
	_ = ctx
	_ = projectID
	return true, nil
}
