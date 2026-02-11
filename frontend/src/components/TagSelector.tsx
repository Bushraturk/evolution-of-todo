import React, { useState, useEffect } from 'react';

export interface Tag {
  id: string;
  name: string;
  color: string;
}

interface TagSelectorProps {
  selectedTags: string[];
  onChange: (tagIds: string[]) => void;
  disabled?: boolean;
}

export default function TagSelector({ selectedTags, onChange, disabled = false }: TagSelectorProps) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [newTagColor, setNewTagColor] = useState('#6366f1');

  useEffect(() => {
    fetchTags();
  }, []);

  const fetchTags = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/tags', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setTags(data.data || []);
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTag = (tagId: string) => {
    if (selectedTags.includes(tagId)) {
      onChange(selectedTags.filter(id => id !== tagId));
    } else {
      onChange([...selectedTags, tagId]);
    }
  };

  const handleCreateTag = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newTagName.trim()) return;

    try {
      const response = await fetch('/api/tags', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          name: newTagName.trim(),
          color: newTagColor,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const newTag = data.data;
        setTags([...tags, newTag]);
        onChange([...selectedTags, newTag.id]);
        setNewTagName('');
        setNewTagColor('#6366f1');
        setShowCreateForm(false);
      }
    } catch (error) {
      console.error('Failed to create tag:', error);
    }
  };

  if (loading) {
    return <div className="text-sm text-gray-500">Loading tags...</div>;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">Tags</label>
        <button
          type="button"
          onClick={() => setShowCreateForm(!showCreateForm)}
          disabled={disabled}
          className="text-xs text-violet-600 hover:text-violet-700"
        >
          {showCreateForm ? 'Cancel' : '+ New Tag'}
        </button>
      </div>

      {showCreateForm && (
        <form onSubmit={handleCreateTag} className="flex gap-2 p-3 bg-gray-50 rounded-lg">
          <input
            type="text"
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            placeholder="Tag name"
            maxLength={50}
            className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded"
          />
          <input
            type="color"
            value={newTagColor}
            onChange={(e) => setNewTagColor(e.target.value)}
            className="w-10 h-8 border border-gray-300 rounded cursor-pointer"
          />
          <button
            type="submit"
            className="px-3 py-1 text-sm bg-violet-600 text-white rounded hover:bg-violet-700"
          >
            Add
          </button>
        </form>
      )}

      <div className="flex flex-wrap gap-2">
        {tags.length === 0 ? (
          <p className="text-sm text-gray-500">No tags yet. Create one to get started!</p>
        ) : (
          tags.map((tag) => (
            <button
              key={tag.id}
              type="button"
              onClick={() => handleToggleTag(tag.id)}
              disabled={disabled}
              className={`px-3 py-1 text-sm rounded-full border-2 transition-all ${
                selectedTags.includes(tag.id)
                  ? 'border-current font-medium'
                  : 'border-transparent opacity-60 hover:opacity-100'
              }`}
              style={{
                backgroundColor: selectedTags.includes(tag.id) ? `${tag.color}20` : `${tag.color}10`,
                color: tag.color,
              }}
            >
              {tag.name}
            </button>
          ))
        )}
      </div>

      {selectedTags.length > 0 && (
        <div className="text-xs text-gray-500">
          {selectedTags.length} tag{selectedTags.length > 1 ? 's' : ''} selected
        </div>
      )}
    </div>
  );
}
