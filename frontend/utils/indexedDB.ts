/**
 * IndexedDB utilities for offline data storage.
 * 
 * Provides a robust offline-first data layer with automatic sync.
 */

const DB_NAME = 'MediFlowDB';
const DB_VERSION = 1;

// Store names
export const STORES = {
  PATIENTS: 'patients',
  APPOINTMENTS: 'appointments',
  PRESCRIPTIONS: 'prescriptions',
  LAB_RESULTS: 'labResults',
  SYNC_QUEUE: 'syncQueue',
  METADATA: 'metadata'
};

/**
 * Initialize IndexedDB database.
 */
export const initDB = (): Promise<IDBDatabase> => {
  return new Promise((resolve, reject) => {
    if (typeof window === 'undefined') {
      reject(new Error('IndexedDB not available in SSR'));
      return;
    }

    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;

      // Create object stores
      if (!db.objectStoreNames.contains(STORES.PATIENTS)) {
        const patientStore = db.createObjectStore(STORES.PATIENTS, { keyPath: 'id' });
        patientStore.createIndex('email', 'email', { unique: true });
        patientStore.createIndex('lastModified', 'lastModified', { unique: false });
      }

      if (!db.objectStoreNames.contains(STORES.APPOINTMENTS)) {
        const appointmentStore = db.createObjectStore(STORES.APPOINTMENTS, { keyPath: 'id' });
        appointmentStore.createIndex('patientId', 'patient_id', { unique: false });
        appointmentStore.createIndex('doctorId', 'doctor_id', { unique: false });
        appointmentStore.createIndex('date', 'appointment_date', { unique: false });
      }

      if (!db.objectStoreNames.contains(STORES.PRESCRIPTIONS)) {
        const prescriptionStore = db.createObjectStore(STORES.PRESCRIPTIONS, { keyPath: 'id' });
        prescriptionStore.createIndex('patientId', 'patient_id', { unique: false });
      }

      if (!db.objectStoreNames.contains(STORES.LAB_RESULTS)) {
        const labStore = db.createObjectStore(STORES.LAB_RESULTS, { keyPath: 'id' });
        labStore.createIndex('patientId', 'patient_id', { unique: false });
      }

      if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
        const syncStore = db.createObjectStore(STORES.SYNC_QUEUE, { keyPath: 'id', autoIncrement: true });
        syncStore.createIndex('timestamp', 'timestamp', { unique: false });
        syncStore.createIndex('synced', 'synced', { unique: false });
      }

      if (!db.objectStoreNames.contains(STORES.METADATA)) {
        db.createObjectStore(STORES.METADATA, { keyPath: 'key' });
      }
    };
  });
};

/**
 * Generic function to add/update data in a store.
 */
export const setItem = async (storeName: string, data: any): Promise<void> => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    
    // Add lastModified timestamp
    const dataWithTimestamp = {
      ...data,
      lastModified: new Date().toISOString()
    };
    
    const request = store.put(dataWithTimestamp);
    
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
};

/**
 * Generic function to get data from a store.
 */
export const getItem = async (storeName: string, id: number | string): Promise<any> => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.get(id);
    
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

/**
 * Generic function to get all data from a store.
 */
export const getAllItems = async (storeName: string): Promise<any[]> => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.getAll();
    
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

/**
 * Generic function to delete data from a store.
 */
export const deleteItem = async (storeName: string, id: number | string): Promise<void> => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.delete(id);
    
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
};

/**
 * Add an operation to the sync queue.
 */
export const addToSyncQueue = async (operation: {
  type: 'CREATE' | 'UPDATE' | 'DELETE';
  storeName: string;
  data: any;
  endpoint: string;
}): Promise<void> => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.SYNC_QUEUE], 'readwrite');
    const store = transaction.objectStore(STORES.SYNC_QUEUE);
    
    const queueItem = {
      ...operation,
      timestamp: new Date().toISOString(),
      synced: false,
      retries: 0
    };
    
    const request = store.add(queueItem);
    
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
};

/**
 * Get all unsynced operations from the queue.
 */
export const getUnsyncedOperations = async (): Promise<any[]> => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.SYNC_QUEUE], 'readonly');
    const store = transaction.objectStore(STORES.SYNC_QUEUE);
    const index = store.index('synced');
    const request = index.getAll(false);
    
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

/**
 * Mark an operation as synced.
 */
export const markAsSynced = async (id: number): Promise<void> => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.SYNC_QUEUE], 'readwrite');
    const store = transaction.objectStore(STORES.SYNC_QUEUE);
    const getRequest = store.get(id);
    
    getRequest.onsuccess = () => {
      const item = getRequest.result;
      if (item) {
        item.synced = true;
        item.syncedAt = new Date().toISOString();
        const putRequest = store.put(item);
        putRequest.onsuccess = () => resolve();
        putRequest.onerror = () => reject(putRequest.error);
      } else {
        resolve();
      }
    };
    
    getRequest.onerror = () => reject(getRequest.error);
  });
};

/**
 * Clear all data from a store.
 */
export const clearStore = async (storeName: string): Promise<void> => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.clear();
    
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
};

/**
 * Get metadata value.
 */
export const getMetadata = async (key: string): Promise<any> => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.METADATA], 'readonly');
    const store = transaction.objectStore(STORES.METADATA);
    const request = store.get(key);
    
    request.onsuccess = () => resolve(request.result?.value);
    request.onerror = () => reject(request.error);
  });
};

/**
 * Set metadata value.
 */
export const setMetadata = async (key: string, value: any): Promise<void> => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.METADATA], 'readwrite');
    const store = transaction.objectStore(STORES.METADATA);
    const request = store.put({ key, value, updatedAt: new Date().toISOString() });
    
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
};

