import React, { useState } from 'react';

export interface ReminderConfig {
  offset_minutes: number;
  channel: 'EMAIL' | 'PUSH' | 'BOTH';
}

interface ReminderFormProps {
  value: ReminderConfig | null;
  onChange: (value: ReminderConfig | null) => void;
  disabled?: boolean;
}

export default function ReminderForm({ value, onChange, disabled = false }: ReminderFormProps) {
  const [enabled, setEnabled] = useState(!!value);

  const handleEnabledChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const isEnabled = e.target.checked;
    setEnabled(isEnabled);

    if (isEnabled) {
      onChange({
        offset_minutes: 30,
        channel: 'EMAIL',
      });
    } else {
      onChange(null);
    }
  };

  const handleOffsetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (value) {
      onChange({
        ...value,
        offset_minutes: parseInt(e.target.value, 10),
      });
    }
  };

  const handleChannelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (value) {
      onChange({
        ...value,
        channel: e.target.value as 'EMAIL' | 'PUSH' | 'BOTH',
      });
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center">
        <input
          type="checkbox"
          id="reminder-enabled"
          checked={enabled}
          onChange={handleEnabledChange}
          disabled={disabled}
          className="h-4 w-4 text-violet-600 focus:ring-violet-500 border-gray-300 rounded"
        />
        <label htmlFor="reminder-enabled" className="ml-2 block text-sm text-gray-700">
          Set reminder
        </label>
      </div>

      {enabled && value && (
        <div className="ml-6 space-y-3">
          <div>
            <label htmlFor="reminder-offset" className="block text-sm font-medium text-gray-700 mb-1">
              Remind me
            </label>
            <select
              id="reminder-offset"
              value={value.offset_minutes}
              onChange={handleOffsetChange}
              disabled={disabled}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-violet-500 focus:border-violet-500 sm:text-sm"
            >
              <option value={5}>5 minutes before</option>
              <option value={15}>15 minutes before</option>
              <option value={30}>30 minutes before</option>
              <option value={60}>1 hour before</option>
              <option value={120}>2 hours before</option>
              <option value={1440}>1 day before</option>
              <option value={2880}>2 days before</option>
              <option value={10080}>1 week before</option>
            </select>
          </div>

          <div>
            <label htmlFor="reminder-channel" className="block text-sm font-medium text-gray-700 mb-1">
              Notification method
            </label>
            <select
              id="reminder-channel"
              value={value.channel}
              onChange={handleChannelChange}
              disabled={disabled}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-violet-500 focus:border-violet-500 sm:text-sm"
            >
              <option value="EMAIL">Email</option>
              <option value="PUSH">Push notification</option>
              <option value="BOTH">Both</option>
            </select>
          </div>

          <div className="text-xs text-gray-500">
            {value.offset_minutes < 60
              ? `You'll be notified ${value.offset_minutes} minutes before the due date`
              : value.offset_minutes < 1440
              ? `You'll be notified ${Math.floor(value.offset_minutes / 60)} hour${Math.floor(value.offset_minutes / 60) > 1 ? 's' : ''} before the due date`
              : `You'll be notified ${Math.floor(value.offset_minutes / 1440)} day${Math.floor(value.offset_minutes / 1440) > 1 ? 's' : ''} before the due date`}
          </div>
        </div>
      )}
    </div>
  );
}
