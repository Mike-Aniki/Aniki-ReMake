using Playnite.SDK;
using Playnite.SDK.Plugins;
using System;
using System.Linq;
using System.Reflection;

namespace YourPlugin.Integration
{
    /// <summary>
    /// Optional bridge to Aniki Helper's on-screen keyboard.
    ///
    /// Add this file directly to your plugin project.
    /// It only references Playnite.SDK and does NOT reference AnikiHelper.dll.
    /// </summary>
    public static class AnikiKeyboardClient
    {
        public static readonly Guid AnikiHelperId =
            Guid.Parse("96a983a3-3f13-4dce-a474-4052b718bb52");

        private const int RequiredApiVersion = 1;

        public static bool IsAvailable(IPlayniteAPI playniteApi)
        {
            Plugin plugin;
            MethodInfo openMethod;
            return TryResolve(playniteApi, out plugin, out openMethod);
        }

        /// <summary>
        /// Opens Aniki Keyboard.
        ///
        /// onSubmit receives:
        ///   text       - final text entered by the user
        ///   pressEnter - true only when the keyboard's "submit + Enter" action was used
        ///
        /// Returns false when Aniki Helper is missing, its API is too old, or another
        /// Aniki keyboard/overlay session currently owns the keyboard.
        /// </summary>
        public static bool TryOpen(
            IPlayniteAPI playniteApi,
            string initialText,
            Action<string, bool> onSubmit,
            Action onCancel = null)
        {
            Plugin plugin;
            MethodInfo openMethod;

            if (!TryResolve(playniteApi, out plugin, out openMethod))
            {
                return false;
            }

            try
            {
                var result = openMethod.Invoke(
                    plugin,
                    new object[]
                    {
                        initialText ?? string.Empty,
                        onSubmit,
                        onCancel
                    });

                return result is bool && (bool)result;
            }
            catch
            {
                return false;
            }
        }

        private static bool TryResolve(
            IPlayniteAPI playniteApi,
            out Plugin plugin,
            out MethodInfo openMethod)
        {
            plugin = null;
            openMethod = null;

            try
            {
                plugin = playniteApi?.Addons?.Plugins?
                    .FirstOrDefault(item => item != null && item.Id == AnikiHelperId);

                if (plugin == null)
                {
                    return false;
                }

                var pluginType = plugin.GetType();

                var versionProperty = pluginType.GetProperty(
                    "AnikiKeyboardApiVersion",
                    BindingFlags.Instance | BindingFlags.Public);

                if (versionProperty == null)
                {
                    return false;
                }

                var rawVersion = versionProperty.GetValue(plugin, null);
                var version = rawVersion is int ? (int)rawVersion : 0;

                if (version < RequiredApiVersion)
                {
                    return false;
                }

                openMethod = pluginType.GetMethod(
                    "OpenAnikiKeyboard",
                    BindingFlags.Instance | BindingFlags.Public,
                    null,
                    new[]
                    {
                        typeof(string),
                        typeof(Action<string, bool>),
                        typeof(Action)
                    },
                    null);

                return openMethod != null;
            }
            catch
            {
                plugin = null;
                openMethod = null;
                return false;
            }
        }
    }
}
