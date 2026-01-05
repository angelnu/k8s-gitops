1. Install OKD Operators
2. Install openshift-local-storage
3. Install ODF
4. Modify ODF console to add the backend

    ```yaml
    displayName: ODF Plugin
    backend:
        type: Service
        service:
        name: odf-console-service
        namespace: openshift-storage
        port: 9001
   ```
5. Create Storage Cluster