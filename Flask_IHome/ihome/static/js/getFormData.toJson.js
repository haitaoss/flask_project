function getFormData(formId) {
            var form = document.getElementById(formId);
            var data = {};
            var tagElements = form.getElementsByTagName('input');
            for (var j = 0; j < tagElements.length; j++) {
                var input = tagElements[j];
                var n = input.name;
                var v = input.value;
                data[n] = v;
            }
            return data;
        }
