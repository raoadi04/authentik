---
title: SCIM source
---

The SCIM source allows other applications to directly create users and groups within authentik. SCIM provides predefined schema for users and groups, with a RESTful API, to enable automatic user provisioning and deprovisioning, SCIM is supported by applications such as Microsoft Azure AD, Google Workspace, and Okta.

The base SCIM URL is in the format of `https://authentik.company/source/scim/<source-slug>/v2`. Authentication is done via Bearer tokens that are generated by authentik. When an SCIM source is created, a service account is created and a matching token is provided.

## Supported Options & Resource types

### `/v2/Users`

Endpoint to list, create, patch, and delete users.

### `/v2/Groups`

Endpoint to list, create, patch, and delete groups.

There is also the `/v2/ServiceProviderConfig` and `/v2/ResourceTypes`, which is used by SCIM-enabled applications to find out which features authentik supports.