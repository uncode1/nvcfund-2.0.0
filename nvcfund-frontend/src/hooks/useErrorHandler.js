import { useGlobalError } from '../contexts/ErrorContext';

/**
 * Hook to access central error handling functionality
 * Provides simplified interface for components
 */
export const useErrorHandler = () => {
  const { showError, hideError, clearError, sanitizeError } = useGlobalError();

  return {
    handleError: showError,
    showError, // Also provide showError for components that use it
    clearError,
    hideError,
    sanitizeError
  };
};