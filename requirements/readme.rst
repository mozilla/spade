Requirements files
==================

pure.txt

   The pure-Python dependencies. This is the requirements file used by
   ``bin/generate-vendor-lib.py`` to generate the bundled vendor library in
   ``vendor``.

compiled.txt

   The compiled dependencies. These are not part of the vendor library and must
   be installed on the target machine either via system/OS packages, or via
   ``pip install -r requirements/compiled.txt``.

gems.txt
   Ruby gems necessary to regenerate CSS from modified Sass files; used by
   ``bin/install-gems``
