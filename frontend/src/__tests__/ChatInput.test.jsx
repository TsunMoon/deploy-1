import { render, screen, fireEvent } from '@testing-library/react';
import ChatInput from '../components/ChatInput';

describe('ChatInput', () => {
  test('renders input and button', () => {
    render(<ChatInput onSend={() => {}} isDisabled={false} />);
    
    expect(screen.getByPlaceholderText('Type your question...')).toBeInTheDocument();
    expect(screen.getByText('Send')).toBeInTheDocument();
  });

  test('button is disabled when input is empty', () => {
    render(<ChatInput onSend={() => {}} isDisabled={false} />);
    
    expect(screen.getByText('Send')).toBeDisabled();
  });

  test('button shows "Wait..." when isDisabled is true', () => {
    render(<ChatInput onSend={() => {}} isDisabled={true} />);
    
    expect(screen.getByText('Wait…')).toBeInTheDocument();
  });

  test('calls onSend with input value when submitted', () => {
    const mockOnSend = jest.fn();
    render(<ChatInput onSend={mockOnSend} isDisabled={false} />);
    
    const input = screen.getByPlaceholderText('Type your question...');
    const button = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'test question' } });
    fireEvent.click(button);

    expect(mockOnSend).toHaveBeenCalledWith('test question');
    expect(input.value).toBe('');
  });
});