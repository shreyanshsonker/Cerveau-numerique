const API_BASE_URL = '/api';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Include cookies for session management
    ...options,
  };

  // Don't set Content-Type for FormData
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
      throw new ApiError(errorData.error || 'Request failed', response.status);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Network error', 0);
  }
}

// Authentication API
export const authApi = {
  register: (userData) => apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  }),

  login: (credentials) => apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  }),

  logout: () => apiRequest('/auth/logout', {
    method: 'POST',
  }),

  getCurrentUser: () => apiRequest('/auth/me'),

  changePassword: (passwordData) => apiRequest('/auth/change-password', {
    method: 'POST',
    body: JSON.stringify(passwordData),
  }),
};

// Tickets API
export const ticketsApi = {
  getTickets: (params = {}) => {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`/tickets?${searchParams}`);
  },

  getTicket: (id) => apiRequest(`/tickets/${id}`),

  createTicket: (formData) => apiRequest('/tickets', {
    method: 'POST',
    body: formData, // FormData for file upload
  }),

  updateTicket: (id, data) => apiRequest(`/tickets/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  addComment: (id, comment) => apiRequest(`/tickets/${id}/comments`, {
    method: 'POST',
    body: JSON.stringify(comment),
  }),

  voteTicket: (id, isUpvote) => apiRequest(`/tickets/${id}/vote`, {
    method: 'POST',
    body: JSON.stringify({ is_upvote: isUpvote }),
  }),

  removeVote: (id) => apiRequest(`/tickets/${id}/vote`, {
    method: 'DELETE',
  }),
};

// Categories API
export const categoriesApi = {
  getCategories: () => apiRequest('/categories'),

  getCategory: (id) => apiRequest(`/categories/${id}`),

  createCategory: (data) => apiRequest('/categories', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  updateCategory: (id, data) => apiRequest(`/categories/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  deleteCategory: (id) => apiRequest(`/categories/${id}`, {
    method: 'DELETE',
  }),
};

// Users API
export const usersApi = {
  getUsers: (params = {}) => {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`/users?${searchParams}`);
  },

  getUser: (id) => apiRequest(`/users/${id}`),

  updateUser: (id, data) => apiRequest(`/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  getAgents: () => apiRequest('/users/agents'),

  deactivateUser: (id) => apiRequest(`/users/${id}/deactivate`, {
    method: 'POST',
  }),

  activateUser: (id) => apiRequest(`/users/${id}/activate`, {
    method: 'POST',
  }),

  getUserStats: () => apiRequest('/users/stats'),
};

export { ApiError };

