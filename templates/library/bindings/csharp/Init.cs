using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using {{crate_name}}.Net.Sys;

// ReSharper disable once CheckNamespace
class Init
{
    [ModuleInitializer]
    internal static void RegisterImportResolver()
    {
        NativeLibrary.SetDllImportResolver(typeof(NativeMethods).Assembly, NativeMethods.DllImportResolver);
    }
}