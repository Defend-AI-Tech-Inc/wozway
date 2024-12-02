# defendai-wozway

<br /><br />

<!-- Start Summary [summary] -->
## Summary

DefendAI Documentation: Wozway Python SDK
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [defendai-wozway](#defendai-wozway)
  * [SDK Installation](#sdk-installation)
  * [SDK Example Usage](#sdk-example-usage)
  * [Authentication](#authentication)
  * [Available Resources and Operations](#available-resources-and-operations)
  * [Error Handling](#error-handling)
  * [Server Selection](#server-selection)
  * [Debugging](#debugging)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

The SDK can be installed with either *pip* package manager.

### PIP


```bash
pip install defendai-wozway
```

<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->

## SDK Example Usage

### Simple Getting Started Example
```python
from defendai_wozway import Wozway
import os

with Wozway(
    bearer_auth=os.getenv("WOZWAY_BEARER_AUTH", ""),
) as s:
    res = s.activities.get_activities()
    if res is not None:
        print(rs)
      pass
```

```python
from defendai_wozway import Wozway
import os

with Wozway(
    bearer_auth=os.getenv("WOZWAY_BEARER_AUTH", ""),
) as s:
    res = s.activities.get_activities(request={
        "search": "Prompt description",
        "filters": "{\"verdicts\":[\"BLOCK\"],\"appNames\":[\"openai-app\"],\"modelNames\":[\"openai\"]}",
    })

    if res is not None:
        # handle response
        pass
```


<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name          | Type  | Scheme      | Environment Variable |
| ------------- |-------| ----------- | -------------------- |
| `bearer_auth` | https | HTTP Bearer | `WOZWAY_BEARER_AUTH` |

To authenticate with the API the `bearer_auth` parameter must be set when initializing the SDK client instance. For example:

<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [activities](docs/sdks/activities/README.md)

* [get_activities](docs/sdks/activities/README.md#get_activities) - Retrieve paginated activity data with filtering, sorting, and search options.

### [api_keys](docs/sdks/apikeys/README.md)

* [delete_api_key](docs/sdks/apikeys/README.md#delete_api_key) - Delete an API key

### [applications](docs/sdks/applications/README.md)

* [get_applications](docs/sdks/applications/README.md#get_applications) - Retrieve a list of applications
* [post_application](docs/sdks/applications/README.md#post_application) - Create or update an application
* [delete_application](docs/sdks/applications/README.md#delete_application) - Delete an application

### [connections](docs/sdks/connections/README.md)

* [post_connection](docs/sdks/connections/README.md#post_connection) - Create or update a connection.
* [delete_connection_id_](docs/sdks/connections/README.md#delete_connection_id_) - Delete a connection by ID.
* [get_connections](docs/sdks/connections/README.md#get_connections) - Retrieve all connections for the user.

### [incidents](docs/sdks/incidents/README.md)

* [post_resolve_incident](docs/sdks/incidents/README.md#post_resolve_incident) - Resolve an incident
* [get_incidents](docs/sdks/incidents/README.md#get_incidents) - Retrieve incident data

### [policies](docs/sdks/policies/README.md)

* [get_policies](docs/sdks/policies/README.md#get_policies) - Retrieve a paginated list of policies with optional filters and sorting.
* [post_policy](docs/sdks/policies/README.md#post_policy) - Create a new policy
* [put_policy](docs/sdks/policies/README.md#put_policy) - Update an existing policy
* [delete_policy](docs/sdks/policies/README.md#delete_policy) - Delete an existing policy

### [users](docs/sdks/users/README.md)

* [post_forgot_password](docs/sdks/users/README.md#post_forgot_password) - Initiate password reset process
* [get_users](docs/sdks/users/README.md#get_users) - Retrieve a list of users
* [post_user](docs/sdks/users/README.md#post_user) - Create a new user.
* [put_user](docs/sdks/users/README.md#put_user) - Update an existing user.
* [delete_user](docs/sdks/users/README.md#delete_user) - Delete a user.


</details>
<!-- End Available Resources and Operations [operations] -->


<!-- Start Error Handling [errors] -->
## Error Handling

Handling errors in this SDK should largely match your expectations. All operations return a response object or raise an exception.

By default, an API error will raise a models.APIError exception, which has the following properties:

| Property        | Type             | Description           |
|-----------------|------------------|-----------------------|
| `.status_code`  | *int*            | The HTTP status code  |
| `.message`      | *str*            | The error message     |
| `.raw_response` | *httpx.Response* | The raw HTTP response |
| `.body`         | *str*            | The response content  |

When custom error responses are specified for an operation, the SDK may also raise their associated exceptions. 
You can refer to respective *Errors* tables in SDK docs for more details on possible exception types for each operation. For example, the `delete_api_key_async` method may raise the following exceptions:

| Error Type                                     | Status Code | Content Type     |
| ---------------------------------------------- | ----------- | ---------------- |
| models.DeleteAPIKeyAPIKeysResponseBody         | 400         | application/json |
| models.DeleteAPIKeyAPIKeysResponseResponseBody | 500         | application/json |
| models.APIError                                | 4XX, 5XX    | \*/\*            |

### Example

```python
from defendai_wozway import Wozway, models
import os

with Wozway(
    bearer_auth=os.getenv("WOZWAY_BEARER_AUTH", ""),
) as s:
    res = None
    try:
        res = s.api_keys.delete_api_key(api_key="<value>")

        if res is not None:
            # handle response
            pass

    except models.DeleteAPIKeyAPIKeysResponseBody as e:
        # handle e.data: models.DeleteAPIKeyAPIKeysResponseBodyData
        raise(e)
    except models.DeleteAPIKeyAPIKeysResponseResponseBody as e:
        # handle e.data: models.DeleteAPIKeyAPIKeysResponseResponseBodyData
        raise(e)
    except models.APIError as e:
        # handle exception
        raise(e)
```
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Select Server by Index

You can override the default server globally by passing a server index to the `server_idx: int` optional parameter when initializing the SDK client instance. The selected server will then be used as the default on the operations that use it. This table lists the indexes associated with the available servers:

| #   | Server                             |
| --- | ---------------------------------- |
| 1   | `https://api.defendai.tech` |

#### Example

```python
from defendai_wozway import Wozway
import os

with Wozway(
    server_idx=1,
    bearer_auth=os.getenv("WOZWAY_BEARER_AUTH", ""),
) as s:
    res = s.activities.get_activities(request={
        "search": "Example text",
        "filters": "{\"verdicts\":[\"BLOCK\"],\"appNames\":[\"app1\",\"app2\"],\"modelNames\":[\"modelA\",\"modelB\"]}",
    })

    if res is not None:
        # handle response
        pass

```

### Override Server URL Per-Client

The default server can also be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from defendai_wozway import Wozway
import os

with Wozway(
    server_url="http://playground.defendai.tech",
    bearer_auth=os.getenv("WOZWAY_BEARER_AUTH", ""),
) as s:
    res = s.activities.get_activities(request={
        "search": "Example text",
        "filters": "{\"verdicts\":[\"BLOCK\"],\"appNames\":[\"app1\",\"app2\"],\"modelNames\":[\"modelA\",\"modelB\"]}",
    })

    if res is not None:
        # handle response
        pass

```
<!-- End Server Selection [server] -->


<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from defendai_wozway import Wozway
import logging

logging.basicConfig(level=logging.DEBUG)
s = Wozway(debug_logger=logging.getLogger("defendai_wozway"))
```

You can also enable a default debug logger by setting an environment variable `WOZWAY_DEBUG` to true.
<!-- End Debugging [debug] -->
