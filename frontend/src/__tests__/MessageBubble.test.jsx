import { render, screen } from '@testing-library/react';
import MessageBubble from '../components/MessageBubble';

describe('MessageBubble', () => {
  test('renders user message correctly', () => {
    const message = {
      role: 'user',
      text: 'Hello there',
      mounted: true,
    };

    render(<MessageBubble message={message} />);
    expect(screen.getByText('Hello there')).toBeInTheDocument();
  });

  test('renders AI message correctly', () => {
    const message = {
      role: 'ai',
      text: 'How can I help?',
      mounted: true,
    };

    render(<MessageBubble message={message} />);
    expect(screen.getByText('How can I help?')).toBeInTheDocument();
  });

  test('shows loading state', () => {
    const message = {
      role: 'ai',
      text: '',
      mounted: true,
      loading: true,
    };

    render(<MessageBubble message={message} />);
    expect(screen.getByText('Thinking...')).toBeInTheDocument();
  });
});