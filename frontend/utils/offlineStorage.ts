/**
 * IndexedDB wrapper for offline data storage
 */

const DB_NAME = 'mediflow-offline'
const DB_VERSION = 1

export interface OfflineOperation {
  id?: number
  type: 'CREATE' | 'UPDATE' | 'DELETE'
  entity: 'patient' | 'appointment' | 'prescription' | 'invoice'
  entityId?: number
  data: any
  timestamp: number
  synced: boolean
}

class OfflineStorage {
  private db: IDBDatabase | null = null

  /**
   * Initialize IndexedDB
   */
  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        this.db = request.result
        resolve()
      }

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result

        // Create object stores
        if (!db.objectStoreNames.contains('patients')) {
          const patientsStore = db.createObjectStore('patients', { keyPath: 'id' })
          patientsStore.createIndex('email', 'email', { unique: false })
          patientsStore.createIndex('updated_at', 'updated_at', { unique: false })
        }

        if (!db.objectStoreNames.contains('appointments')) {
          const appointmentsStore = db.createObjectStore('appointments', { keyPath: 'id' })
          appointmentsStore.createIndex('patient_id', 'patient_id', { unique: false })
          appointmentsStore.createIndex('appointment_date', 'appointment_date', { unique: false })
        }

        if (!db.objectStoreNames.contains('prescriptions')) {
          const prescriptionsStore = db.createObjectStore('prescriptions', { keyPath: 'id' })
          prescriptionsStore.createIndex('patient_id', 'patient_id', { unique: false })
        }

        if (!db.objectStoreNames.contains('pending_operations')) {
          db.createObjectStore('pending_operations', { keyPath: 'id', autoIncrement: true })
        }
      }
    })
  }

  /**
   * Save data to IndexedDB
   */
  async save<T>(storeName: string, data: T): Promise<void> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.put(data)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve()
    })
  }

  /**
   * Get data from IndexedDB
   */
  async get<T>(storeName: string, key: number): Promise<T | undefined> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const request = store.get(key)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result)
    })
  }

  /**
   * Get all data from a store
   */
  async getAll<T>(storeName: string): Promise<T[]> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const request = store.getAll()

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result)
    })
  }

  /**
   * Delete data from IndexedDB
   */
  async delete(storeName: string, key: number): Promise<void> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.delete(key)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve()
    })
  }

  /**
   * Clear all data from a store
   */
  async clear(storeName: string): Promise<void> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.clear()

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve()
    })
  }

  /**
   * Add pending operation for sync
   */
  async addPendingOperation(operation: OfflineOperation): Promise<number> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['pending_operations'], 'readwrite')
      const store = transaction.objectStore('pending_operations')
      const request = store.add(operation)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result as number)
    })
  }

  /**
   * Get all pending operations
   */
  async getPendingOperations(): Promise<OfflineOperation[]> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['pending_operations'], 'readonly')
      const store = transaction.objectStore('pending_operations')
      const request = store.getAll()

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result)
    })
  }

  /**
   * Remove pending operation after sync
   */
  async removePendingOperation(id: number): Promise<void> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['pending_operations'], 'readwrite')
      const store = transaction.objectStore('pending_operations')
      const request = store.delete(id)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve()
    })
  }

  /**
   * Search by index
   */
  async searchByIndex<T>(
    storeName: string,
    indexName: string,
    value: any
  ): Promise<T[]> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const index = store.index(indexName)
      const request = index.getAll(value)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result)
    })
  }
}

// Singleton instance
export const offlineStorage = new OfflineStorage()

/**
 * Hook for using offline storage
 */
export function useOfflineStorage() {
  const isOnline = typeof navigator !== 'undefined' ? navigator.onLine : true

  const saveOffline = async <T>(storeName: string, data: T) => {
    try {
      await offlineStorage.save(storeName, data)
      console.log(`[OfflineStorage] Saved to ${storeName}:`, data)
    } catch (error) {
      console.error('[OfflineStorage] Save failed:', error)
      throw error
    }
  }

  const getOffline = async <T>(storeName: string, key: number) => {
    try {
      return await offlineStorage.get<T>(storeName, key)
    } catch (error) {
      console.error('[OfflineStorage] Get failed:', error)
      throw error
    }
  }

  const getAllOffline = async <T>(storeName: string) => {
    try {
      return await offlineStorage.getAll<T>(storeName)
    } catch (error) {
      console.error('[OfflineStorage] GetAll failed:', error)
      throw error
    }
  }

  const queueOperation = async (operation: OfflineOperation) => {
    try {
      const id = await offlineStorage.addPendingOperation(operation)
      console.log('[OfflineStorage] Queued operation:', id)
      
      // Trigger background sync if available
      if ('serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
        const registration = await navigator.serviceWorker.ready
        await registration.sync.register('sync-data')
      }
      
      return id
    } catch (error) {
      console.error('[OfflineStorage] Queue operation failed:', error)
      throw error
    }
  }

  return {
    isOnline,
    saveOffline,
    getOffline,
    getAllOffline,
    queueOperation,
  }
}

