package stream

import "sync"

type Broker struct {
	mu   sync.RWMutex
	subs map[string][]chan string
}

func NewBroker() *Broker {
	return &Broker{subs: map[string][]chan string{}}
}

func (b *Broker) Subscribe(projectID string) chan string {
	ch := make(chan string, 16)
	b.mu.Lock()
	b.subs[projectID] = append(b.subs[projectID], ch)
	b.mu.Unlock()
	return ch
}

func (b *Broker) Unsubscribe(projectID string, target chan string) {
	b.mu.Lock()
	defer b.mu.Unlock()
	current := b.subs[projectID]
	next := make([]chan string, 0, len(current))
	for _, ch := range current {
		if ch == target {
			close(ch)
			continue
		}
		next = append(next, ch)
	}
	b.subs[projectID] = next
}

func (b *Broker) Publish(projectID, msg string) {
	b.mu.RLock()
	defer b.mu.RUnlock()
	for _, ch := range b.subs[projectID] {
		select {
		case ch <- msg:
		default:
		}
	}
}
