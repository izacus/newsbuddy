Known installaton issues
++++++++++++++++++++++++


I have an error on pip install!!
--------------------------------

Make sure you can access the libmemcache while installing.

I have an error `ImportError: No module named _sqlite3`!!
---------------------------------------------------------

Make sure you have python with sqlite3 compiled and the .so linked.


I have and invalid ELF on libLemmatizer.so or lib!!
---------------------------------------------------

Use ldd to debug which libs are missing.
And them patchelf to patch them or link to the compiled lemmatizer.

::

    patchelf --set-rpath /nix/store/sha1_hash/lib/ mining/lemmatizer/libLemmatizer.so
