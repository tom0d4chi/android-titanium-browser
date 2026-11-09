#!/usr/bin/env python3
"""Adds the "Phone interface" switch (Settings > Appearance).

When on: the browser lays out like a phone even on a wide/unfolded screen
(no tab strip, phone toolbar + tab switcher button, bottom bar).
Run from chromium/src. Every edit asserts it matched exactly once.
"""
import sys

PREF = "titanium_phone_ui"


def edit(path, old, new, count=1):
    s = open(path, encoding="utf-8").read()
    n = s.count(old)
    if n != count:
        sys.exit(f"phone_ui: {path}: expected {count} match(es), found {n} for: {old[:70]!r}")
    open(path, "w", encoding="utf-8").write(s.replace(old, new))


# 1. Width bucket: report "phone" (0) when the switch is on.
DFF = "ui/android/java/src/org/chromium/ui/base/DeviceFormFactor.java"
edit(DFF,
     "    private static int detectScreenWidthBucket(Context context) {\n",
     "    private static boolean isPhoneUiForced() {\n"
     "        try {\n"
     "            return ContextUtils.getAppSharedPreferences().getBoolean(\"%s\", false);\n"
     "        } catch (Throwable t) {\n"
     "            return false;\n"
     "        }\n"
     "    }\n\n"
     "    private static int detectScreenWidthBucket(Context context) {\n"
     "        if (isPhoneUiForced()) return 0;\n" % PREF)
edit(DFF,
     "        if (context == null) return 0;\n        return context.getResources()",
     "        if (context == null) return 0;\n        if (isPhoneUiForced()) return 0;\n        return context.getResources()")

# 2. Settings row.
edit("chrome/android/java/res/xml/appearance_preferences.xml",
     "</PreferenceScreen>",
     "    <org.chromium.components.browser_ui.settings.ChromeSwitchPreference\n"
     "        android:key=\"phone_ui_switch\"\n"
     "        android:order=\"5\"\n"
     "        android:title=\"Interface t\u00e9l\u00e9phone\"\n"
     "        android:summary=\"Navigation en bas, sans barre d\u2019onglets (red\u00e9marrage requis)\" />\n\n"
     "</PreferenceScreen>")

FRAG = "chrome/android/java/src/org/chromium/chrome/browser/appearance/settings/AppearanceSettingsFragment.java"
edit(FRAG,
     "        initTabPositionPref();\n    }\n",
     "        initTabPositionPref();\n        initPhoneUiPref();\n    }\n\n"
     "    @SuppressWarnings(\"UseSharedPreferencesManagerFromChromeCheck\")\n"
     "    private void initPhoneUiPref() {\n"
     "        ChromeSwitchPreference sw = findPreference(\"phone_ui_switch\");\n"
     "        if (sw == null) return;\n"
     "        sw.setChecked(ContextUtils.getAppSharedPreferences().getBoolean(\"%s\", false));\n"
     "        sw.setOnPreferenceChangeListener(\n"
     "                (pref, newValue) -> {\n"
     "                    ContextUtils.getAppSharedPreferences()\n"
     "                            .edit()\n"
     "                            .putBoolean(\"%s\", (boolean) newValue)\n"
     "                            .commit();\n"
     "                    android.widget.Toast.makeText(\n"
     "                                    getContext(),\n"
     "                                    \"Ferme puis rouvre le navigateur pour appliquer\",\n"
     "                                    android.widget.Toast.LENGTH_LONG)\n"
     "                            .show();\n"
     "                    return true;\n"
     "                });\n"
     "    }\n" % (PREF, PREF))

# 3. Bottom bar on by default (flag was off in stable builds).
edit("chrome/browser/flags/android/chrome_feature_list.cc",
     "BASE_FEATURE(kAndroidBottomBar, base::FEATURE_DISABLED_BY_DEFAULT);",
     "BASE_FEATURE(kAndroidBottomBar, base::FEATURE_ENABLED_BY_DEFAULT);")
edit("chrome/browser/flags/android/java/src/org/chromium/chrome/browser/flags/ChromeFeatureList.java",
     "newCachedFlag(ANDROID_BOTTOM_BAR, false, /* defaultValueInTests= */ true);",
     "newCachedFlag(ANDROID_BOTTOM_BAR, true, /* defaultValueInTests= */ true);")
print("phone_ui: OK")
