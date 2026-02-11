import React, { useState } from 'react';
import { format } from 'date-fns';

interface DateTimePickerProps {
  value: string | null;
  onChange: (value: string | null) => void;
  label?: string;
  minDate?: string;
}

export default function DateTimePicker({
  value,
  onChange,
  label = 'Due date',
  minDate,
}: DateTimePickerProps) {
  const [isEnabled, setIsEnabled] = useState(!!value);
  const [date, setDate] = useState(
    value ? format(new Date(value), 'yyyy-MM-dd') : ''
  );
  const [time, setTime] = useState(
    value ? format(new Date(value), 'HH:mm') : '09:00'
  );

  const handleToggle = () => {
    const newEnabled = !isEnabled;
    setIsEnabled(newEnabled);

    if (newEnabled) {
      const today = format(new Date(), 'yyyy-MM-dd');
      setDate(today);
      updateDateTime(today, time);
    } else {
      onChange(null);
    }
  };

  const updateDateTime = (newDate: string, newTime: string) => {
    if (newDate && newTime) {
      const dateTime = `${newDate}T${newTime}:00Z`;
      onChange(dateTime);
    }
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDate = e.target.value;
    setDate(newDate);
    updateDateTime(newDate, time);
  };

  const handleTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = e.target.value;
    setTime(newTime);
    updateDateTime(date, newTime);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="due-date"
          checked={isEnabled}
          onChange={handleToggle}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="due-date" className="text-sm font-medium text-gray-700">
          Set {label.toLowerCase()}
        </label>
      </div>

      {isEnabled && (
        <div className="ml-6 grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date
            </label>
            <input
              type="date"
              value={date}
              min={minDate}
              onChange={handleDateChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time
            </label>
            <input
              type="time"
              value={time}
              onChange={handleTimeChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      )}
    </div>
  );
}
