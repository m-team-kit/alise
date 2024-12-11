# ALISE Endpoints

All api endpoints are `get` requests.

The following replacements are made:

- `{site}`: the short name of the configured local site you're using
- `{subiss}`: `"urlencode(sub)@urlencode(iss)"`
- `{encoded_sub}`: `"urlencode(sub)"`
- `{encoded_iss}`: `"urlencode(iss)"`

## `/api/v1/{site}/get_mappings/{subiss}`

- Deprecated
- Return all mappings that match a given `sub + iss` pair

## `/api/v1/target/{site}/mapping/issuer/{encoded_iss}/user/{encoded_sub}?apikey=<apikey>`

- Return all mappings that match a given `sub + iss` pair
- Pass the `apikey` as a URL parameter

## `/api/v1/version`

- Return the version of alise

## `/api/v1/authenticated`

- For checking if api user was authenticated
- Pass the `Access Token` via: `"Authorization: Bearer ${ACCESS_TOKEN}"`

## `/api/v1/all_my_mappings_raw`

- Internal, do not use


## `/api/v1/target/{site}/get_apikey`

- Return an `apikey`, which is associated to a specific user, identified
    by an `Access Token`
- Pass the `Access Token` via: `"Authorization: Bearer ${ACCESS_TOKEN}"`


## `/api/v1/target/{site}/validate_apikey/{apikey}`

- For testing the `apikey`


## `/api/v1/alise/supported_issuers`

- List all supported issuers (internal and external ones)
