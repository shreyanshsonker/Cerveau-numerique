import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ticketsApi, usersApi } from '../../lib/api';
import { 
  ArrowLeft, 
  MessageSquare, 
  ThumbsUp, 
  ThumbsDown, 
  Calendar,
  User,
  Tag,
  Clock,
  Send,
  Download
} from 'lucide-react';
import LoadingSpinner from '../ui/LoadingSpinner';

const TicketDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAdmin, isSupportAgent, isEndUser } = useAuth();
  
  const [ticket, setTicket] = useState(null);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newComment, setNewComment] = useState('');
  const [commentLoading, setCommentLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchTicket();
    if (isAdmin || isSupportAgent) {
      fetchAgents();
    }
  }, [id]);

  const fetchTicket = async () => {
    try {
      setLoading(true);
      const response = await ticketsApi.getTicket(id);
      setTicket(response.ticket);
    } catch (error) {
      setError('Failed to fetch ticket details');
      console.error('Fetch ticket error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAgents = async () => {
    try {
      const response = await usersApi.getAgents();
      setAgents(response.agents);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      setUpdating(true);
      await ticketsApi.updateTicket(id, { status: newStatus });
      await fetchTicket(); // Refresh ticket data
    } catch (error) {
      setError('Failed to update ticket status');
    } finally {
      setUpdating(false);
    }
  };

  const handleAssignmentChange = async (assignedTo) => {
    try {
      setUpdating(true);
      await ticketsApi.updateTicket(id, { assigned_to: assignedTo || null });
      await fetchTicket(); // Refresh ticket data
    } catch (error) {
      setError('Failed to update ticket assignment');
    } finally {
      setUpdating(false);
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      setCommentLoading(true);
      await ticketsApi.addComment(id, { content: newComment.trim() });
      setNewComment('');
      await fetchTicket(); // Refresh to show new comment
    } catch (error) {
      setError('Failed to add comment');
    } finally {
      setCommentLoading(false);
    }
  };

  const handleVote = async (isUpvote) => {
    try {
      await ticketsApi.voteTicket(id, isUpvote);
      await fetchTicket(); // Refresh to show updated votes
    } catch (error) {
      setError('Failed to record vote');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open':
        return 'bg-red-100 text-red-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'resolved':
        return 'bg-green-100 text-green-800';
      case 'closed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'text-red-600';
      case 'high':
        return 'text-orange-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-green-600';
      default:
        return 'text-gray-600';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Ticket not found</h3>
        <p className="mt-1 text-sm text-gray-500">
          The ticket you're looking for doesn't exist or you don't have permission to view it.
        </p>
        <div className="mt-6">
          <Link
            to="/tickets"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Tickets
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/tickets')}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Tickets
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Ticket Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-gray-900">
                #{ticket.id} {ticket.subject}
              </h1>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}>
                {ticket.status.replace('_', ' ')}
              </span>
              <span className={`text-sm font-medium ${getPriorityColor(ticket.priority)}`}>
                {ticket.priority} priority
              </span>
            </div>
            
            <div className="mt-4 flex items-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center">
                <User className="h-4 w-4 mr-1" />
                Created by {ticket.creator?.username}
              </div>
              <div className="flex items-center">
                <Calendar className="h-4 w-4 mr-1" />
                {formatDate(ticket.created_at)}
              </div>
              <div className="flex items-center">
                <Tag className="h-4 w-4 mr-1" />
                {ticket.category?.name}
              </div>
              {ticket.assignee && (
                <div className="flex items-center">
                  <User className="h-4 w-4 mr-1" />
                  Assigned to {ticket.assignee.username}
                </div>
              )}
            </div>
          </div>

          {/* Voting */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleVote(true)}
              className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-md"
            >
              <ThumbsUp className="h-4 w-4" />
              <span>{ticket.upvotes}</span>
            </button>
            <button
              onClick={() => handleVote(false)}
              className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-md"
            >
              <ThumbsDown className="h-4 w-4" />
              <span>{ticket.downvotes}</span>
            </button>
          </div>
        </div>

        {/* Agent Controls */}
        {(isAdmin || isSupportAgent) && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="status" className="block text-sm font-medium text-gray-700">
                  Status
                </label>
                <select
                  id="status"
                  value={ticket.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  disabled={updating}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <div>
                <label htmlFor="assigned_to" className="block text-sm font-medium text-gray-700">
                  Assigned To
                </label>
                <select
                  id="assigned_to"
                  value={ticket.assigned_to || ''}
                  onChange={(e) => handleAssignmentChange(e.target.value)}
                  disabled={updating}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="">Unassigned</option>
                  {agents.map((agent) => (
                    <option key={agent.id} value={agent.id}>
                      {agent.username}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Ticket Description */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Description</h3>
        <div className="prose max-w-none">
          <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
        </div>
        
        {ticket.attachment_path && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center">
              <Download className="h-5 w-5 text-gray-400 mr-2" />
              <a
                href={`/api/static/${ticket.attachment_path}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-500"
              >
                Download Attachment
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Comments */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Comments ({ticket.comments?.length || 0})
        </h3>

        {/* Comment Form */}
        {(ticket.user_id === user?.id || isAdmin || isSupportAgent) && (
          <form onSubmit={handleAddComment} className="mb-6">
            <div>
              <label htmlFor="comment" className="sr-only">
                Add a comment
              </label>
              <textarea
                id="comment"
                rows={3}
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Add a comment..."
              />
            </div>
            <div className="mt-3 flex justify-end">
              <button
                type="submit"
                disabled={commentLoading || !newComment.trim()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {commentLoading ? (
                  <LoadingSpinner size="sm" className="mr-2" />
                ) : (
                  <Send className="mr-2 h-4 w-4" />
                )}
                Add Comment
              </button>
            </div>
          </form>
        )}

        {/* Comments List */}
        <div className="space-y-4">
          {ticket.comments?.map((comment) => (
            <div key={comment.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-900">
                    {comment.author?.username}
                  </span>
                  <span className="text-sm text-gray-500">
                    {formatDate(comment.created_at)}
                  </span>
                </div>
              </div>
              <p className="text-gray-700 whitespace-pre-wrap">{comment.content}</p>
            </div>
          ))}
          
          {(!ticket.comments || ticket.comments.length === 0) && (
            <p className="text-gray-500 text-center py-4">No comments yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TicketDetail;

