/**
 * Sync Manager for offline-first data synchronization.
 * 
 * Handles automatic sync between IndexedDB and backend API.
 */

import axios from 'axios';
import {
  getUnsyncedOperations,
  markAsSynced,
  setItem,
  getMetadata,
  setMetadata,
  STORES
} from './indexedDB';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class SyncManager {
  private syncInProgress = false;
  private syncInterval: NodeJS.Timeout | null = null;

  /**
   * Start automatic sync (every 30 seconds when online).
   */
  startAutoSync(intervalMs: number = 30000): void {
    if (this.syncInterval) {
      return; // Already running
    }

    this.syncInterval = setInterval(() => {
      if (navigator.onLine) {
        this.syncAll();
      }
    }, intervalMs);

    // Also sync immediately if online
    if (navigator.onLine) {
      this.syncAll();
    }
  }

  /**
   * Stop automatic sync.
   */
  stopAutoSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  /**
   * Sync all pending operations.
   */
  async syncAll(): Promise<{ success: number; failed: number }> {
    if (this.syncInProgress) {
      console.log('Sync already in progress, skipping...');
      return { success: 0, failed: 0 };
    }

    if (!navigator.onLine) {
      console.log('Offline, skipping sync...');
      return { success: 0, failed: 0 };
    }

    this.syncInProgress = true;
    let successCount = 0;
    let failedCount = 0;

    try {
      const operations = await getUnsyncedOperations();
      console.log(`Syncing ${operations.length} operations...`);

      for (const operation of operations) {
        try {
          await this.syncOperation(operation);
          await markAsSynced(operation.id);
          successCount++;
        } catch (error) {
          console.error('Failed to sync operation:', operation, error);
          failedCount++;
          
          // Increment retry count
          operation.retries = (operation.retries || 0) + 1;
          
          // If too many retries, mark as failed
          if (operation.retries >= 5) {
            await markAsSynced(operation.id); // Remove from queue
            console.error('Operation failed after 5 retries:', operation);
          }
        }
      }

      // Update last sync timestamp
      await setMetadata('lastSyncTime', new Date().toISOString());

      console.log(`Sync complete: ${successCount} success, ${failedCount} failed`);
    } catch (error) {
      console.error('Sync error:', error);
    } finally {
      this.syncInProgress = false;
    }

    return { success: successCount, failed: failedCount };
  }

  /**
   * Sync a single operation.
   */
  private async syncOperation(operation: any): Promise<void> {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No authentication token');
    }

    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    switch (operation.type) {
      case 'CREATE':
        await axios.post(`${API_BASE_URL}${operation.endpoint}`, operation.data, { headers });
        break;

      case 'UPDATE':
        await axios.put(`${API_BASE_URL}${operation.endpoint}`, operation.data, { headers });
        break;

      case 'DELETE':
        await axios.delete(`${API_BASE_URL}${operation.endpoint}`, { headers });
        break;

      default:
        throw new Error(`Unknown operation type: ${operation.type}`);
    }
  }

  /**
   * Pull latest data from server and update local cache.
   */
  async pullFromServer(): Promise<void> {
    if (!navigator.onLine) {
      console.log('Offline, cannot pull from server');
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No authentication token');
    }

    const headers = {
      'Authorization': `Bearer ${token}`
    };

    try {
      // Pull patients
      const patientsResponse = await axios.get(`${API_BASE_URL}/patients?page=1&page_size=100`, { headers });
      if (patientsResponse.data.items) {
        for (const patient of patientsResponse.data.items) {
          await setItem(STORES.PATIENTS, patient);
        }
      }

      // Pull appointments
      const appointmentsResponse = await axios.get(`${API_BASE_URL}/appointments?page=1&page_size=100`, { headers });
      if (appointmentsResponse.data.items) {
        for (const appointment of appointmentsResponse.data.items) {
          await setItem(STORES.APPOINTMENTS, appointment);
        }
      }

      // Pull prescriptions
      const prescriptionsResponse = await axios.get(`${API_BASE_URL}/prescriptions?page=1&page_size=100`, { headers });
      if (prescriptionsResponse.data.items) {
        for (const prescription of prescriptionsResponse.data.items) {
          await setItem(STORES.PRESCRIPTIONS, prescription);
        }
      }

      // Pull lab results
      const labResultsResponse = await axios.get(`${API_BASE_URL}/lab-results?page=1&page_size=100`, { headers });
      if (labResultsResponse.data.items) {
        for (const labResult of labResultsResponse.data.items) {
          await setItem(STORES.LAB_RESULTS, labResult);
        }
      }

      await setMetadata('lastPullTime', new Date().toISOString());
      console.log('Successfully pulled data from server');
    } catch (error) {
      console.error('Failed to pull from server:', error);
      throw error;
    }
  }

  /**
   * Get sync status.
   */
  async getSyncStatus(): Promise<{
    lastSyncTime: string | null;
    lastPullTime: string | null;
    pendingOperations: number;
    isOnline: boolean;
  }> {
    const lastSyncTime = await getMetadata('lastSyncTime');
    const lastPullTime = await getMetadata('lastPullTime');
    const operations = await getUnsyncedOperations();

    return {
      lastSyncTime,
      lastPullTime,
      pendingOperations: operations.length,
      isOnline: navigator.onLine
    };
  }
}

// Export singleton instance
export const syncManager = new SyncManager();

// Auto-start sync when module loads (browser only)
if (typeof window !== 'undefined') {
  // Start sync after a short delay to allow app initialization
  setTimeout(() => {
    syncManager.startAutoSync();
  }, 2000);

  // Listen for online/offline events
  window.addEventListener('online', () => {
    console.log('Back online, syncing...');
    syncManager.syncAll();
  });

  window.addEventListener('offline', () => {
    console.log('Gone offline, sync paused');
  });
}

