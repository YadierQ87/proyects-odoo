import re

import phonenumbers
import validators


class FieldValidator:
    def validate(self, post, validator_list):
        errors = {}
        for field, validator_type in validator_list.items():
            if not post.get(field):
                continue
            validation_result = getattr(self, validator_type)(post.get(field))
            if "error" in validation_result:
                errors.update({field: validation_result["error"]})
        return errors

    def validate_url(self, term):
        if not validators.url(term):
            return {"error": "URL incorrecta"}
        return {}

    def validate_email(self, term):
        if not validators.email(term):
            return {"error": "Email incorrecto"}
        return {}

    def validate_alphanumeric_with_spaces(self, term):
        if not re.fullmatch(r"[A-Za-z\d\s]+", term):
            return {"error": "El valor del campo no es válido."}
        return {}

    def validate_phone(self, term):
        try:
            parse_number = phonenumbers.parse(term)
            if phonenumbers.is_possible_number(parse_number):
                is_semantic_valid = phonenumbers.is_valid_number(parse_number)
                if not is_semantic_valid:
                    return {"error": "El teléfono no es válido."}
                return {}
            else:
                return {"error": "El teléfono no es válido."}
        except Exception as e:
            return {"error": str(e)}

    def validate_facebook(self, term):
        if not re.fullmatch(
            r"(?:(?:http|https):\/\/)?(?:www\.)?facebook\.com\/([\w\.])+", term
        ):
            return {"error": "URL de perfil de facebook inválida"}
        return {}

    def validate_linkedin(self, term):
        if not re.fullmatch(
            r"(?:(?:http|https):\/\/)?(?:www\.)?linkedin\.com\/([\w\.])+", term
        ):
            return {"error": "URL de perfil de linkedin inválida"}
        return {}

    def validate_date(self):
        pass
