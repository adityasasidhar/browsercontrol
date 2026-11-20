# Fill a form

Use the latest element map to fill fields and confirm the browser reached the
expected result. To practice with sample data, use the
[demo form from the first session](../getting-started/first-session.md).

## Fill the fields

1. Open the form with `navigate_to(url)` and locate the first field by its label.
2. Call [`type_text(element_id, text)`](../tools/interaction.md#type_text).
   It replaces the existing value in an input, textarea, or editable region.
3. Find the next field in the returned map and repeat. If a field is below the
   viewport, scroll and look for it in the new map.

## Select options and attach files

| Control | How to use it |
| --- | --- |
| Native dropdown | Use [`select_option`](../tools/forms.md#select_option) with the visible label or option value. |
| Checkbox | Use [`check_checkbox`](../tools/forms.md#check_checkbox) with `check=True` to check it or `check=False` to clear it. |
| Custom dropdown | Open it with `click`, then find and click the option in the updated map. Keyboard navigation may also work. |
| File input | Use [`upload_file`](upload-files.md) with an absolute path. |

## Submit and verify

Find Submit in the latest element map and call `click` with its current ID.
Use the returned screenshot or `get_page_content()` to check for a
confirmation message or validation errors. If the response is still loading,
wait briefly and check again.
