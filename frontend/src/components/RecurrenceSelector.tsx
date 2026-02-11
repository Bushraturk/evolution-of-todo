import React, { useState } from 'react';

interface RecurrenceConfig {
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
  interval: number;
  dayOfWeek?: number;
  dayOfMonth?: number;
  endDate?: string;
}

interface RecurrenceSelectorProps {
  value: RecurrenceConfig | null;
  onChange: (value: RecurrenceConfig | null) => void;
}

const DAYS_OF_WEEK = [
  { value: 0, label: 'Sunday' },
  { value: 1, label: 'Monday' },
  { value: 2, label: 'Tuesday' },
  { value: 3, label: 'Wednesday' },
  { value: 4, label: 'Thursday' },
  { value: 5, label: 'Friday' },
  { value: 6, label: 'Saturday' },
];

export default function RecurrenceSelector({ value, onChange }: RecurrenceSelectorProps) {
  const [isEnabled, setIsEnabled] = useState(!!value);
  const [frequency, setFrequency] = useState<'DAILY' | 'WEEKLY' | 'MONTHLY'>(
    value?.frequency || 'DAILY'
  );
  const [interval, setInterval] = useState(value?.interval || 1);
  const [dayOfWeek, setDayOfWeek] = useState(value?.dayOfWeek ?? 1);
  const [dayOfMonth, setDayOfMonth] = useState(value?.dayOfMonth ?? 1);
  const [endDate, setEndDate] = useState(value?.endDate || '');

  const handleToggle = () => {
    const newEnabled = !isEnabled;
    setIsEnabled(newEnabled);

    if (newEnabled) {
      updateRecurrence();
    } else {
      onChange(null);
    }
  };

  const updateRecurrence = () => {
    const config: RecurrenceConfig = {
      frequency,
      interval,
      ...(frequency === 'WEEKLY' && { dayOfWeek }),
      ...(frequency === 'MONTHLY' && { dayOfMonth }),
      ...(endDate && { endDate }),
    };
    onChange(config);
  };

  React.useEffect(() => {
    if (isEnabled) {
      updateRecurrence();
    }
  }, [frequency, interval, dayOfWeek, dayOfMonth, endDate]);

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="recurring"
          checked={isEnabled}
          onChange={handleToggle}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="recurring" className="text-sm font-medium text-gray-700">
          Repeat this task
        </label>
      </div>

      {isEnabled && (
        <div className="ml-6 space-y-4 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Frequency
              </label>
              <select
                value={frequency}
                onChange={(e) => setFrequency(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="DAILY">Daily</option>
                <option value="WEEKLY">Weekly</option>
                <option value="MONTHLY">Monthly</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Every
              </label>
              <input
                type="number"
                min="1"
                value={interval}
                onChange={(e) => setInterval(parseInt(e.target.value) || 1)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {frequency === 'WEEKLY' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                On day
              </label>
              <select
                value={dayOfWeek}
                onChange={(e) => setDayOfWeek(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {DAYS_OF_WEEK.map((day) => (
                  <option key={day.value} value={day.value}>
                    {day.label}
                  </option>
                ))}
              </select>
            </div>
          )}

          {frequency === 'MONTHLY' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                On day of month
              </label>
              <input
                type="number"
                min="1"
                max="31"
                value={dayOfMonth}
                onChange={(e) => setDayOfMonth(parseInt(e.target.value) || 1)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End date (optional)
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded">
            <strong>Summary:</strong> Repeats every {interval}{' '}
            {frequency === 'DAILY' && `day${interval > 1 ? 's' : ''}`}
            {frequency === 'WEEKLY' &&
              `week${interval > 1 ? 's' : ''} on ${
                DAYS_OF_WEEK.find((d) => d.value === dayOfWeek)?.label
              }`}
            {frequency === 'MONTHLY' &&
              `month${interval > 1 ? 's' : ''} on day ${dayOfMonth}`}
            {endDate && ` until ${new Date(endDate).toLocaleDateString()}`}
          </div>
        </div>
      )}
    </div>
  );
}
