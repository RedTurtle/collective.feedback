Changelog
=========


1.1.2 (2024-03-15)
------------------

- Fix typo in actions.xml permission.
  [cekk]


1.1.1 (2024-03-13)
------------------

- re-add actions.xml file to have a user-action needed on Volto.
  [cekk]


1.1.0 (2024-03-12)
------------------

- Only managers can access deleted feedbacks.
  [cekk]
- Allow all authenticated users to access @feedback endpoint.
  The endpoint will return only feedbacks on objects that they can edit.
  [cekk]
- Improve tests.
  [cekk]
- Install souper.plone to have its control-panel in backend.
  [cekk]
- Remove unused user action.
  [cekk]
- Add `actions` infos in @feedback endpoint, to let the frontend know what the user can do.
  [cekk]

1.0.0 (2023-02-16)
------------------

- Initial release.
  [eikichi18]
