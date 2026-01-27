'use client';

interface ConfirmDialogProps {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-purple-950/50 backdrop-blur-sm">
      <div className="glass-strong rounded-2xl shadow-2xl max-w-sm w-full p-6">
        <h2 className="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-2">
          {title}
        </h2>
        <p className="text-purple-600 dark:text-purple-300 mb-6">
          {message}
        </p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="btn-secondary"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className="btn-danger"
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
