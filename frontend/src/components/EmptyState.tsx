export default function EmptyState() {
  return (
    <div className="text-center py-12 card">
      <svg
        className="mx-auto h-16 w-16 text-purple-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
        />
      </svg>
      <h3 className="mt-4 text-lg font-semibold text-purple-900 dark:text-purple-100">
        No tasks yet
      </h3>
      <p className="mt-2 text-sm text-purple-500 dark:text-purple-400">
        Get started by creating your first task.
      </p>
    </div>
  );
}
