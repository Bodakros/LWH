import api from '../lib/api/client';
import { endpoints, getUrlWithParams } from '../lib/api/endpoints';

/**
 * Service for interacting with the inventory API
 */
const inventoryService = {
    /**
     * Get inventory items with filtering and pagination
     * @param {Object} params - request parameters
     * @param {number} params.product - product ID filter
     * @param {number} params.stock - stock ID filter
     * @param {number} params.warehouse - warehouse ID filter
     * @param {string} params.status - status filter
     * @param {string} params.batch_number - batch number filter
     * @param {number} params.page - page number
     * @param {number} params.page_size - items per page
     * @returns {Promise} - promise with request results
     */
    getInventoryItems: async (params = {}) => {
        const queryParams = new URLSearchParams();

        // Add parameters to the request
        if (params.product) queryParams.append('product', params.product);
        if (params.stock) queryParams.append('stock', params.stock);
        if (params.warehouse) queryParams.append('warehouse', params.warehouse);
        if (params.status) queryParams.append('status', params.status);
        if (params.batch_number) queryParams.append('batch_number', params.batch_number);
        if (params.page) queryParams.append('page', params.page);
        if (params.page_size) queryParams.append('page_size', params.page_size);

        return api.get(`${endpoints.inventory.items}?${queryParams.toString()}`);
    },

    /**
     * Get inventory item details by ID
     * @param {number} id - inventory item ID
     * @returns {Promise} - promise with request results
     */
    getInventoryItemById: async (id) => {
        return api.get(getUrlWithParams(endpoints.inventory.itemDetail, { pk: id }));
    },

    /**
     * Create inventory item
     * @param {Object} itemData - Inventory item data
     * @returns {Promise} - promise with request results
     */
    createInventoryItem: async (itemData) => {
        return api.post(endpoints.inventory.items, itemData);
    },

    /**
     * Update inventory item
     * @param {number} id - inventory item ID
     * @param {Object} itemData - Inventory item data to update
     * @returns {Promise} - promise with request results
     */
    updateInventoryItem: async (id, itemData) => {
        return api.put(getUrlWithParams(endpoints.inventory.itemDetail, { pk: id }), itemData);
    },

    /**
     * Delete inventory item
     * @param {number} id - inventory item ID
     * @returns {Promise} - promise with request results
     */
    deleteInventoryItem: async (id) => {
        return api.delete(getUrlWithParams(endpoints.inventory.itemDetail, { pk: id }));
    },

    /**
     * Get inventory movements with filtering and pagination
     * @param {Object} params - request parameters
     * @param {number} params.product - product ID filter
     * @param {number} params.source_stock - source stock ID filter
     * @param {number} params.destination_stock - destination stock ID filter
     * @param {string} params.reason - reason filter
     * @param {number} params.page - page number
     * @param {number} params.page_size - items per page
     * @returns {Promise} - promise with request results
     */
    getInventoryMovements: async (params = {}) => {
        const queryParams = new URLSearchParams();

        // Add parameters to the request
        if (params.product) queryParams.append('product', params.product);
        if (params.source_stock) queryParams.append('source_stock', params.source_stock);
        if (params.destination_stock) queryParams.append('destination_stock', params.destination_stock);
        if (params.reason) queryParams.append('reason', params.reason);
        if (params.page) queryParams.append('page', params.page);
        if (params.page_size) queryParams.append('page_size', params.page_size);

        return api.get(`${endpoints.inventory.movements}?${queryParams.toString()}`);
    },

    /**
     * Get inventory movement details by ID
     * @param {number} id - inventory movement ID
     * @returns {Promise} - promise with request results
     */
    getInventoryMovementById: async (id) => {
        return api.get(getUrlWithParams(endpoints.inventory.movementDetail, { pk: id }));
    },

    /**
     * Create inventory movement
     * @param {Object} movementData - Inventory movement data
     * @returns {Promise} - promise with request results
     */
    createInventoryMovement: async (movementData) => {
        return api.post(endpoints.inventory.movements, movementData);
    },

    /**
     * Get inventory audits with filtering and pagination
     * @param {Object} params - request parameters
     * @param {number} params.inventory_item - inventory item ID filter
     * @param {boolean} params.resolved - resolved status filter
     * @param {number} params.page - page number
     * @param {number} params.page_size - items per page
     * @returns {Promise} - promise with request results
     */
    getInventoryAudits: async (params = {}) => {
        const queryParams = new URLSearchParams();

        // Add parameters to the request
        if (params.inventory_item) queryParams.append('inventory_item', params.inventory_item);
        if (params.resolved !== undefined) queryParams.append('resolved', params.resolved);
        if (params.page) queryParams.append('page', params.page);
        if (params.page_size) queryParams.append('page_size', params.page_size);

        return api.get(`${endpoints.inventory.audits}?${queryParams.toString()}`);
    },

    /**
     * Get inventory audit details by ID
     * @param {number} id - inventory audit ID
     * @returns {Promise} - promise with request results
     */
    getInventoryAuditById: async (id) => {
        return api.get(getUrlWithParams(endpoints.inventory.auditDetail, { pk: id }));
    },

    /**
     * Create inventory audit
     * @param {Object} auditData - Inventory audit data
     * @returns {Promise} - promise with request results
     */
    createInventoryAudit: async (auditData) => {
        return api.post(endpoints.inventory.audits, auditData);
    },

    /**
     * Update inventory audit
     * @param {number} id - inventory audit ID
     * @param {Object} auditData - Inventory audit data to update
     * @returns {Promise} - promise with request results
     */
    updateInventoryAudit: async (id, auditData) => {
        return api.put(getUrlWithParams(endpoints.inventory.auditDetail, { pk: id }), auditData);
    },

    /**
     * Get receiving records with filtering and pagination
     * @param {Object} params - request parameters
     * @param {number} params.warehouse - warehouse ID filter
     * @param {string} params.status - status filter
     * @param {number} params.page - page number
     * @param {number} params.page_size - items per page
     * @returns {Promise} - promise with request results
     */
    getReceivingRecords: async (params = {}) => {
        const queryParams = new URLSearchParams();

        // Add parameters to the request
        if (params.warehouse) queryParams.append('warehouse', params.warehouse);
        if (params.status) queryParams.append('status', params.status);
        if (params.page) queryParams.append('page', params.page);
        if (params.page_size) queryParams.append('page_size', params.page_size);

        return api.get(`${endpoints.inventory.receiving}?${queryParams.toString()}`);
    },

    /**
     * Get receiving record details by ID
     * @param {number} id - receiving record ID
     * @returns {Promise} - promise with request results
     */
    getReceivingRecordById: async (id) => {
        return api.get(getUrlWithParams(endpoints.inventory.receivingDetail, { pk: id }));
    },

    /**
     * Create receiving record
     * @param {Object} recordData - Receiving record data
     * @returns {Promise} - promise with request results
     */
    createReceivingRecord: async (recordData) => {
        return api.post(endpoints.inventory.receiving, recordData);
    },

    /**
     * Update receiving record
     * @param {number} id - receiving record ID
     * @param {Object} recordData - Receiving record data to update
     * @returns {Promise} - promise with request results
     */
    updateReceivingRecord: async (id, recordData) => {
        return api.put(getUrlWithParams(endpoints.inventory.receivingDetail, { pk: id }), recordData);
    },

    /**
     * Delete receiving record
     * @param {number} id - receiving record ID
     * @returns {Promise} - promise with request results
     */
    deleteReceivingRecord: async (id) => {
        return api.delete(getUrlWithParams(endpoints.inventory.receivingDetail, { pk: id }));
    },

    /**
     * Get receiving items for a receiving record
     * @param {number} receivingRecordId - receiving record ID
     * @returns {Promise} - promise with request results
     */
    getReceivingItems: async (receivingRecordId) => {
        return api.get(getUrlWithParams(endpoints.inventory.receivingItems, { receiving_record_id: receivingRecordId }));
    },

    /**
     * Get receiving item details by ID
     * @param {number} receivingRecordId - receiving record ID
     * @param {number} id - receiving item ID
     * @returns {Promise} - promise with request results
     */
    getReceivingItemById: async (receivingRecordId, id) => {
        return api.get(getUrlWithParams(endpoints.inventory.receivingItemDetail, {
            receiving_record_id: receivingRecordId,
            pk: id
        }));
    },

    /**
     * Create receiving item
     * @param {number} receivingRecordId - receiving record ID
     * @param {Object} itemData - Receiving item data
     * @returns {Promise} - promise with request results
     */
    createReceivingItem: async (receivingRecordId, itemData) => {
        return api.post(
            getUrlWithParams(endpoints.inventory.receivingItems, { receiving_record_id: receivingRecordId }),
            itemData
        );
    },

    /**
     * Update receiving item
     * @param {number} receivingRecordId - receiving record ID
     * @param {number} id - receiving item ID
     * @param {Object} itemData - Receiving item data to update
     * @returns {Promise} - promise with request results
     */
    updateReceivingItem: async (receivingRecordId, id, itemData) => {
        return api.put(
            getUrlWithParams(endpoints.inventory.receivingItemDetail, {
                receiving_record_id: receivingRecordId,
                pk: id
            }),
            itemData
        );
    },

    /**
     * Delete receiving item
     * @param {number} receivingRecordId - receiving record ID
     * @param {number} id - receiving item ID
     * @returns {Promise} - promise with request results
     */
    deleteReceivingItem: async (receivingRecordId, id) => {
        return api.delete(
            getUrlWithParams(endpoints.inventory.receivingItemDetail, {
                receiving_record_id: receivingRecordId,
                pk: id
            })
        );
    },

    /**
     * Receive item (create inventory record)
     * @param {number} receivingRecordId - receiving record ID
     * @param {number} id - receiving item ID
     * @returns {Promise} - promise with request results
     */
    receiveItem: async (receivingRecordId, id) => {
        return api.post(
            getUrlWithParams(endpoints.inventory.receiveItem, {
                receiving_record_id: receivingRecordId,
                pk: id
            })
        );
    }
};

export default inventoryService;