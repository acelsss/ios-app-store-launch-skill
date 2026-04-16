# Privacy Policy And App Privacy Guidance

Use this reference when drafting privacy pages and App Store Connect App Privacy answers.

## Conservative Rule

Do not state "no data collected" until the final binary has been checked for:

- Analytics SDKs.
- Advertising SDKs.
- Crash reporting SDKs.
- Account/login systems.
- Server uploads or API calls involving user data.
- Tracking or cross-app identifiers.
- Third-party storage or processing.

## Local Processing Language

If true, say that processing is performed locally on the user's device and that the developer does not automatically receive the user's data.

Avoid wording that implies the developer may receive exported files. A safer pattern:

> The app does not provide any remote access channel for the developer to access this data. If the user exports or shares files, files are sent only through the method and to the recipients the user chooses.

## Permission Sections

For location:

- Explain what the app uses location for.
- Explain background location if requested.
- Explain local storage and clear/export controls if applicable.

For photos:

- Explain what photo access is used for.
- Explain whether photos are modified, copied, or read-only.
- Explain skip behavior when relevant.

## Required Contact

Include developer name and contact email in every privacy page.
