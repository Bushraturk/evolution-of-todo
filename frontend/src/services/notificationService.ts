/**
 * Notification Service - Handles push notification subscriptions
 */

const VAPID_PUBLIC_KEY = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || '';

export interface PushSubscription {
  endpoint: string;
  keys: {
    p256dh: string;
    auth: string;
  };
}

class NotificationService {
  private registration: ServiceWorkerRegistration | null = null;

  /**
   * Check if push notifications are supported
   */
  isSupported(): boolean {
    return (
      'serviceWorker' in navigator &&
      'PushManager' in window &&
      'Notification' in window
    );
  }

  /**
   * Request notification permission from user
   */
  async requestPermission(): Promise<NotificationPermission> {
    if (!this.isSupported()) {
      throw new Error('Push notifications are not supported');
    }

    const permission = await Notification.requestPermission();
    return permission;
  }

  /**
   * Register service worker
   */
  async registerServiceWorker(): Promise<ServiceWorkerRegistration> {
    if (!this.isSupported()) {
      throw new Error('Service workers are not supported');
    }

    if (this.registration) {
      return this.registration;
    }

    try {
      this.registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service worker registered:', this.registration);
      return this.registration;
    } catch (error) {
      console.error('Service worker registration failed:', error);
      throw error;
    }
  }

  /**
   * Subscribe to push notifications
   */
  async subscribe(): Promise<PushSubscription | null> {
    if (!this.isSupported()) {
      throw new Error('Push notifications are not supported');
    }

    // Request permission
    const permission = await this.requestPermission();
    if (permission !== 'granted') {
      console.log('Notification permission denied');
      return null;
    }

    // Register service worker
    const registration = await this.registerServiceWorker();

    // Subscribe to push notifications
    try {
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      });

      // Convert to our format
      const pushSubscription: PushSubscription = {
        endpoint: subscription.endpoint,
        keys: {
          p256dh: this.arrayBufferToBase64(subscription.getKey('p256dh')!),
          auth: this.arrayBufferToBase64(subscription.getKey('auth')!),
        },
      };

      console.log('Push subscription created:', pushSubscription);
      return pushSubscription;
    } catch (error) {
      console.error('Failed to subscribe to push notifications:', error);
      throw error;
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribe(): Promise<boolean> {
    if (!this.registration) {
      return false;
    }

    try {
      const subscription = await this.registration.pushManager.getSubscription();
      if (subscription) {
        const result = await subscription.unsubscribe();
        console.log('Unsubscribed from push notifications:', result);
        return result;
      }
      return false;
    } catch (error) {
      console.error('Failed to unsubscribe from push notifications:', error);
      return false;
    }
  }

  /**
   * Get current push subscription
   */
  async getSubscription(): Promise<PushSubscription | null> {
    if (!this.registration) {
      return null;
    }

    try {
      const subscription = await this.registration.pushManager.getSubscription();
      if (!subscription) {
        return null;
      }

      return {
        endpoint: subscription.endpoint,
        keys: {
          p256dh: this.arrayBufferToBase64(subscription.getKey('p256dh')!),
          auth: this.arrayBufferToBase64(subscription.getKey('auth')!),
        },
      };
    } catch (error) {
      console.error('Failed to get push subscription:', error);
      return null;
    }
  }

  /**
   * Convert URL-safe base64 to Uint8Array
   */
  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  /**
   * Convert ArrayBuffer to base64
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }
}

export const notificationService = new NotificationService();
